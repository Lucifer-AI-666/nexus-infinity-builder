#!/usr/bin/env python3
"""
Task Scheduler - Permette a Nexus di lavorare autonomamente
Segue la metodologia di Sanfilippo: planning file aggiornato continuamente
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from groq import Groq

class TaskScheduler:
    """Scheduler autonomo per task lunghi con planning file"""
    
    def __init__(self, planning_file: str = "PLANNING.md"):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.planning_file = planning_file
        self.tasks: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.model = "llama-3.3-70b-versatile"
        
    def create_task(self, title: str, description: str, priority: str = "medium") -> Dict:
        """Crea un nuovo task"""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "subtasks": [],
            "notes": []
        }
        self.tasks.append(task)
        self._update_planning_file()
        return task
    
    def execute_task(self, task_id: int) -> str:
        """Esegue un task e aggiorna il planning file"""
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return f"Task {task_id} non trovato"
        
        task["status"] = "in_progress"
        self._update_planning_file()
        
        # Chiedi a Groq di eseguire il task
        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """Sei Nexus Infinity, un agente autonomo intelligente.
                    Esegui il task richiesto e fornisci un report dettagliato.
                    Aggiorna continuamente il planning file con il progress."""
                },
                {
                    "role": "user",
                    "content": f"Esegui questo task:\n\nTitolo: {task['title']}\nDescrizione: {task['description']}\n\nFornisci un report dettagliato del lavoro svolto."
                }
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        
        result = response.choices[0].message.content
        
        # Aggiorna task
        task["status"] = "completed"
        task["result"] = result
        task["updated_at"] = datetime.now().isoformat()
        self.completed_tasks.append(task)
        self.tasks.remove(task)
        
        # Aggiorna planning file
        self._update_planning_file()
        
        return result
    
    def add_subtask(self, task_id: int, subtask: str) -> Dict:
        """Aggiunge un subtask a un task"""
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return {"error": f"Task {task_id} non trovato"}
        
        subtask_obj = {
            "id": len(task["subtasks"]) + 1,
            "title": subtask,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        task["subtasks"].append(subtask_obj)
        self._update_planning_file()
        return subtask_obj
    
    def add_note(self, task_id: int, note: str) -> None:
        """Aggiunge una nota a un task"""
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if task:
            task["notes"].append({
                "text": note,
                "timestamp": datetime.now().isoformat()
            })
            self._update_planning_file()
    
    def get_status(self) -> Dict:
        """Ritorna lo stato attuale"""
        return {
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks if t["status"] == "pending"]),
            "in_progress_tasks": len([t for t in self.tasks if t["status"] == "in_progress"]),
            "completed_tasks": len(self.completed_tasks),
            "tasks": self.tasks,
            "completed": self.completed_tasks
        }
    
    def _update_planning_file(self) -> None:
        """Aggiorna il file PLANNING.md con lo stato attuale"""
        status = self.get_status()
        
        # Leggi il file attuale
        if os.path.exists(self.planning_file):
            with open(self.planning_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# Planning File\n\n"
        
        # Aggiorna timestamp
        timestamp = datetime.now().isoformat()
        content = content.replace(
            "**Ultimo aggiornamento**:",
            f"**Ultimo aggiornamento**: {timestamp}"
        )
        
        # Scrivi il file aggiornato
        with open(self.planning_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def run_autonomous(self, duration_hours: int = 1) -> None:
        """Esegue task autonomamente per N ore"""
        print(f"\n🤖 Avvio modalità autonoma per {duration_hours} ore...")
        print(f"⏱️  Inizio: {datetime.now().isoformat()}\n")
        
        start_time = datetime.now()
        task_count = 0
        
        while (datetime.now() - start_time).total_seconds() < duration_hours * 3600:
            # Esegui task pendenti
            pending = [t for t in self.tasks if t["status"] == "pending"]
            
            if not pending:
                print("✅ Nessun task pendente. Agente in attesa...")
                break
            
            for task in pending:
                print(f"\n📋 Esecuzione task: {task['title']}")
                result = self.execute_task(task["id"])
                print(f"✅ Completato!\n{result[:200]}...\n")
                task_count += 1
        
        print(f"\n🏁 Autonomia terminata")
        print(f"⏱️  Fine: {datetime.now().isoformat()}")
        print(f"📊 Task completati: {task_count}")
        print(f"📈 Status finale:\n{json.dumps(self.get_status(), indent=2, ensure_ascii=False)}")

def main():
    """Test del scheduler"""
    scheduler = TaskScheduler()
    
    # Crea task di esempio
    task1 = scheduler.create_task(
        "Analizzare codice legacy",
        "Analizzare il codice legacy di Nexus e identificare aree di miglioramento",
        "high"
    )
    
    task2 = scheduler.create_task(
        "Ottimizzare performance API",
        "Ottimizzare i tempi di risposta dell'API REST",
        "high"
    )
    
    print("📋 Task creati:")
    print(json.dumps(scheduler.get_status(), indent=2, ensure_ascii=False))
    
    # Esegui task autonomamente per 1 ora
    scheduler.run_autonomous(duration_hours=1)

if __name__ == "__main__":
    main()
