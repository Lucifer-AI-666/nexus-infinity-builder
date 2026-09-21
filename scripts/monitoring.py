#!/usr/bin/env python3
"""
Monitoring & Logging - Traccia tutto quello che fa l'agente
Audit log completo, performance metrics, error tracking
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
from enum import Enum

class EventType(Enum):
    """Tipi di eventi da tracciare"""
    API_CALL = "api_call"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TASK_ERROR = "task_error"
    DECISION = "decision"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESULT = "approval_result"
    MEMORY_SAVE = "memory_save"
    CHECKPOINT_CREATE = "checkpoint_create"

class NexusMonitor:
    """Sistema di monitoring e logging"""
    
    def __init__(self, logs_dir: str = "nexus_logs"):
        self.logs_dir = logs_dir
        os.makedirs(logs_dir, exist_ok=True)
        
        self.audit_log_file = os.path.join(logs_dir, "audit.log")
        self.events_file = os.path.join(logs_dir, "events.json")
        self.metrics_file = os.path.join(logs_dir, "metrics.json")
        
        # Setup logging
        self.logger = logging.getLogger("NexusInfinity")
        handler = logging.FileHandler(self.audit_log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        self._initialize_files()
    
    def _initialize_files(self):
        """Inizializza i file di logging"""
        if not os.path.exists(self.events_file):
            with open(self.events_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w') as f:
                json.dump({"start_time": datetime.now().isoformat(), "events": {}}, f)
    
    def log_event(self, event_type: EventType, description: str, 
                 data: Dict = None, severity: str = "info"):
        """Registra un evento"""
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "description": description,
            "severity": severity,
            "data": data or {}
        }
        
        # Salva nel file events.json
        with open(self.events_file, 'r') as f:
            events = json.load(f)
        events.append(event)
        with open(self.events_file, 'w') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        # Log nel file audit.log
        log_level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(log_level, f"[{event_type.value}] {description}")
        
        # Aggiorna metriche
        self._update_metrics(event_type)
    
    def _update_metrics(self, event_type: EventType):
        """Aggiorna le metriche"""
        with open(self.metrics_file, 'r') as f:
            metrics = json.load(f)
        
        if event_type.value not in metrics["events"]:
            metrics["events"][event_type.value] = 0
        
        metrics["events"][event_type.value] += 1
        metrics["last_updated"] = datetime.now().isoformat()
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                    response_time: float):
        """Registra una chiamata API"""
        self.log_event(
            EventType.API_CALL,
            f"{method} {endpoint} -> {status_code}",
            {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time * 1000
            }
        )
    
    def log_task_start(self, task_id: str, task_name: str):
        """Registra l'inizio di un task"""
        self.log_event(
            EventType.TASK_START,
            f"Task avviato: {task_name}",
            {"task_id": task_id, "task_name": task_name}
        )
    
    def log_task_complete(self, task_id: str, task_name: str, duration: float):
        """Registra il completamento di un task"""
        self.log_event(
            EventType.TASK_COMPLETE,
            f"Task completato: {task_name}",
            {
                "task_id": task_id,
                "task_name": task_name,
                "duration_seconds": duration
            }
        )
    
    def log_task_error(self, task_id: str, task_name: str, error: str):
        """Registra un errore di task"""
        self.log_event(
            EventType.TASK_ERROR,
            f"Errore in task: {task_name}",
            {
                "task_id": task_id,
                "task_name": task_name,
                "error": error
            },
            severity="error"
        )
    
    def log_decision(self, decision: str, reasoning: str):
        """Registra una decisione"""
        self.log_event(
            EventType.DECISION,
            f"Decisione: {decision}",
            {"decision": decision, "reasoning": reasoning}
        )
    
    def get_events(self, limit: int = 100) -> list:
        """Recupera gli ultimi eventi"""
        with open(self.events_file, 'r') as f:
            events = json.load(f)
        return events[-limit:]
    
    def get_metrics(self) -> Dict:
        """Recupera le metriche"""
        with open(self.metrics_file, 'r') as f:
            return json.load(f)
    
    def get_audit_log(self, lines: int = 50) -> str:
        """Recupera le ultime righe dell'audit log"""
        with open(self.audit_log_file, 'r') as f:
            all_lines = f.readlines()
        return ''.join(all_lines[-lines:])
    
    def print_summary(self):
        """Stampa un riepilogo"""
        metrics = self.get_metrics()
        
        print("\n" + "="*60)
        print("📊 NEXUS INFINITY - MONITORING SUMMARY")
        print("="*60)
        print(f"Start Time: {metrics['start_time']}")
        print(f"Last Updated: {metrics['last_updated']}")
        print("\nEvent Counts:")
        for event_type, count in metrics['events'].items():
            print(f"  - {event_type}: {count}")
        print("="*60 + "\n")

if __name__ == "__main__":
    monitor = NexusMonitor()
    
    # Test
    monitor.log_event(EventType.TASK_START, "Test task avviato")
    monitor.log_api_call("/api/chat", "POST", 200, 0.15)
    monitor.log_task_complete("task_1", "Test task", 5.2)
    monitor.log_decision("Usare Groq", "Performance ottimale")
    
    monitor.print_summary()
