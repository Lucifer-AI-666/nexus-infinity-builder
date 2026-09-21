#!/usr/bin/env python3
"""
Approval Gate - Feedback loop umano per azioni sensibili
L'agente chiede approvazione prima di azioni importanti
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from enum import Enum

class ActionType(Enum):
    """Tipi di azioni che richiedono approvazione"""
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"
    EXTERNAL_API = "external_api"
    DATABASE_WRITE = "database_write"
    DEPLOY = "deploy"

class ApprovalStatus(Enum):
    """Status di un'approvazione"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ApprovalGate:
    """Gestisce le approvazioni umane"""
    
    def __init__(self, approvals_dir: str = "nexus_approvals"):
        self.approvals_dir = approvals_dir
        os.makedirs(approvals_dir, exist_ok=True)
        self.approvals_file = os.path.join(approvals_dir, "approvals.json")
        
        if not os.path.exists(self.approvals_file):
            with open(self.approvals_file, 'w') as f:
                json.dump([], f)
    
    def request_approval(self, action_type: ActionType, description: str, 
                        details: Dict = None, urgency: str = "normal") -> str:
        """Richiede approvazione per un'azione"""
        
        approval_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        with open(self.approvals_file, 'r') as f:
            approvals = json.load(f)
        
        approval = {
            "id": approval_id,
            "action_type": action_type.value,
            "description": description,
            "details": details or {},
            "urgency": urgency,
            "status": ApprovalStatus.PENDING.value,
            "requested_at": datetime.now().isoformat(),
            "approved_at": None,
            "approved_by": None,
            "rejection_reason": None
        }
        
        approvals.append(approval)
        
        with open(self.approvals_file, 'w') as f:
            json.dump(approvals, f, indent=2, ensure_ascii=False)
        
        print(f"\n🔐 RICHIESTA DI APPROVAZIONE")
        print(f"ID: {approval_id}")
        print(f"Tipo: {action_type.value}")
        print(f"Descrizione: {description}")
        print(f"Urgenza: {urgency}")
        print(f"\nDettagli: {json.dumps(details, indent=2, ensure_ascii=False)}")
        print(f"\nIn attesa di approvazione umana...\n")
        
        return approval_id
    
    def approve(self, approval_id: str, approved_by: str = "admin"):
        """Approva un'azione"""
        with open(self.approvals_file, 'r') as f:
            approvals = json.load(f)
        
        approval = next((a for a in approvals if a["id"] == approval_id), None)
        if not approval:
            return {"error": f"Approvazione {approval_id} non trovata"}
        
        approval["status"] = ApprovalStatus.APPROVED.value
        approval["approved_at"] = datetime.now().isoformat()
        approval["approved_by"] = approved_by
        
        with open(self.approvals_file, 'w') as f:
            json.dump(approvals, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Approvazione {approval_id} APPROVATA")
        return approval
    
    def reject(self, approval_id: str, reason: str, rejected_by: str = "admin"):
        """Rifiuta un'azione"""
        with open(self.approvals_file, 'r') as f:
            approvals = json.load(f)
        
        approval = next((a for a in approvals if a["id"] == approval_id), None)
        if not approval:
            return {"error": f"Approvazione {approval_id} non trovata"}
        
        approval["status"] = ApprovalStatus.REJECTED.value
        approval["rejection_reason"] = reason
        approval["approved_by"] = rejected_by
        
        with open(self.approvals_file, 'w') as f:
            json.dump(approvals, f, indent=2, ensure_ascii=False)
        
        print(f"❌ Approvazione {approval_id} RIFIUTATA")
        print(f"Motivo: {reason}")
        return approval
    
    def get_pending_approvals(self) -> List[Dict]:
        """Elenca le approvazioni in sospeso"""
        with open(self.approvals_file, 'r') as f:
            approvals = json.load(f)
        
        return [a for a in approvals if a["status"] == ApprovalStatus.PENDING.value]
    
    def get_approval_status(self, approval_id: str) -> Dict:
        """Ottiene lo status di un'approvazione"""
        with open(self.approvals_file, 'r') as f:
            approvals = json.load(f)
        
        approval = next((a for a in approvals if a["id"] == approval_id), None)
        return approval or {"error": "Non trovata"}
    
    def get_approval_history(self) -> List[Dict]:
        """Ottiene la cronologia di tutte le approvazioni"""
        with open(self.approvals_file, 'r') as f:
            approvals = json.load(f)
        
        return sorted(approvals, key=lambda x: x["requested_at"], reverse=True)

if __name__ == "__main__":
    gate = ApprovalGate()
    
    # Test
    approval_id = gate.request_approval(
        ActionType.MODIFY_FILE,
        "Modificare il file main.py",
        {"file": "main.py", "changes": "Aggiungere logging"},
        "high"
    )
    
    print(f"\nApprovazioni in sospeso: {len(gate.get_pending_approvals())}")
    
    # Simula approvazione
    gate.approve(approval_id)
    
    print(f"\nApprovazioni in sospeso dopo approvazione: {len(gate.get_pending_approvals())}")
