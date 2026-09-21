#!/usr/bin/env python3
"""
Persistent Memory System - Memoria a lungo termine per l'agente
Salva stato, conversazioni, decisioni tra sessioni
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List

class PersistentMemory:
    """Gestisce la memoria persistente dell'agente"""
    
    def __init__(self, memory_dir: str = "nexus_memory"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        self.conversation_file = os.path.join(memory_dir, "conversations.json")
        self.state_file = os.path.join(memory_dir, "state.json")
        self.decisions_file = os.path.join(memory_dir, "decisions.json")
        self.checkpoints_file = os.path.join(memory_dir, "checkpoints.json")
        
        self._initialize_files()
    
    def _initialize_files(self):
        """Inizializza i file di memoria"""
        for file_path in [self.conversation_file, self.state_file, 
                         self.decisions_file, self.checkpoints_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def save_conversation(self, role: str, content: str, metadata: Dict = None):
        """Salva una conversazione"""
        with open(self.conversation_file, 'r') as f:
            conversations = json.load(f)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        conversations.append(entry)
        
        with open(self.conversation_file, 'w') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    def get_conversations(self, limit: int = 100) -> List[Dict]:
        """Recupera le ultime conversazioni"""
        with open(self.conversation_file, 'r') as f:
            conversations = json.load(f)
        return conversations[-limit:]
    
    def save_state(self, state: Dict):
        """Salva lo stato attuale dell'agente"""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_state(self) -> Dict:
        """Carica lo stato salvato"""
        with open(self.state_file, 'r') as f:
            content = f.read()
        if not content or content.strip() == '[]':
            return {}
        states = json.loads(content)
        return states[-1] if isinstance(states, list) and len(states) > 0 else (states if isinstance(states, dict) else {})
    
    def save_decision(self, decision: str, reasoning: str, outcome: str = None):
        """Salva una decisione importante"""
        with open(self.decisions_file, 'r') as f:
            decisions = json.load(f)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "reasoning": reasoning,
            "outcome": outcome
        }
        decisions.append(entry)
        
        with open(self.decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2, ensure_ascii=False)
    
    def get_decisions(self) -> List[Dict]:
        """Recupera tutte le decisioni"""
        with open(self.decisions_file, 'r') as f:
            return json.load(f)
    
    def create_checkpoint(self, name: str, data: Dict) -> str:
        """Crea un checkpoint"""
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(self.checkpoints_file, 'r') as f:
            checkpoints = json.load(f)
        
        checkpoint = {
            "id": checkpoint_id,
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        checkpoints.append(checkpoint)
        
        with open(self.checkpoints_file, 'w') as f:
            json.dump(checkpoints, f, indent=2, ensure_ascii=False)
        
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Dict:
        """Carica un checkpoint"""
        with open(self.checkpoints_file, 'r') as f:
            checkpoints = json.load(f)
        
        checkpoint = next((c for c in checkpoints if c["id"] == checkpoint_id), None)
        return checkpoint["data"] if checkpoint else None
    
    def get_checkpoints(self) -> List[Dict]:
        """Elenca tutti i checkpoint"""
        with open(self.checkpoints_file, 'r') as f:
            checkpoints = json.load(f)
        return checkpoints
    
    def clear_memory(self):
        """Cancella tutta la memoria"""
        for file_path in [self.conversation_file, self.state_file, 
                         self.decisions_file, self.checkpoints_file]:
            with open(file_path, 'w') as f:
                json.dump([], f)
    
    def get_memory_stats(self) -> Dict:
        """Statistiche della memoria"""
        with open(self.conversation_file, 'r') as f:
            conversations = json.load(f)
        with open(self.decisions_file, 'r') as f:
            decisions = json.load(f)
        with open(self.checkpoints_file, 'r') as f:
            checkpoints = json.load(f)
        
        return {
            "total_conversations": len(conversations),
            "total_decisions": len(decisions),
            "total_checkpoints": len(checkpoints),
            "memory_dir": self.memory_dir
        }

if __name__ == "__main__":
    memory = PersistentMemory()
    
    # Test
    memory.save_conversation("user", "Ciao Nexus!")
    memory.save_conversation("assistant", "Ciao! Come posso aiutarti?")
    memory.save_decision("Usare Groq", "Performance ultra-veloce", "✅ Implementato")
    memory.save_state({"status": "online", "tasks_completed": 5})
    
    print("📊 Memory Stats:")
    print(json.dumps(memory.get_memory_stats(), indent=2))
