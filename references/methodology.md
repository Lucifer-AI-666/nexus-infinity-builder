# Metodologia Nexus Infinity Builder

## Principi Fondamentali (Sanfilippo)

### 1. Planning File Continuo
L'agente deve mantenere un file `PLANNING.md` aggiornato continuamente con:
- Roadmap principale (fasi del progetto)
- Task correnti con checklist
- Metriche di progresso
- Log delle sessioni
- Decisioni architetturali

**Formato consigliato:**
```markdown
# Planning File

**Ultimo aggiornamento**: ISO timestamp

## Roadmap Principale
- [x] Fase 1: Core
- [ ] Fase 2: Autonomia
- [ ] Fase 3: Scalabilità

## Task Correnti
- [ ] Task 1: Descrizione
- [ ] Task 2: Descrizione
```

### 2. Architetture su Misura (Harness Custom)
- **NO**: Framework generici e riutilizzabili
- **SÌ**: Harness strettamente legati al progetto specifico
- Ogni componente è parte integrante dell'applicazione
- Massima flessibilità e performance ottimale

### 3. Autonomia con Checkpoint
- L'agente lavora autonomamente per ore o giorni
- Salva checkpoint regolari per ripresa
- Aggiorna il planning file continuamente
- Mantiene memoria persistente tra sessioni

### 4. Comunicazione Empatica
- Trattare l'IA come interlocutore umano
- Prompt chiari e gentili
- Feedback positivo per risultati migliori
- Modellare uno stato emotivo (frustrazione, rabbia) non significa "provarlo"

### 5. Human-in-the-Loop
- Mantenere controllo umano per azioni critiche
- Approval Gate per modifiche sensibili
- Richieste di approvazione esplicite
- Cronologia completa delle decisioni

## Architettura Standard di Nexus Infinity

### Layer 1: Core Intelligente
```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    temperature=0.7,
    max_tokens=2048
)
```

### Layer 2: Persistent Memory
- `memory.py`: Gestisce conversazioni, stato, checkpoint
- File JSON per persistenza
- Caricamento automatico da sessioni precedenti

### Layer 3: Approval Gate
- `approval_gate.py`: Richieste di approvazione
- ID univoci per ogni richiesta
- Stati: pending, approved, rejected

### Layer 4: Task Scheduler
- `task_scheduler.py`: Gestione autonoma dei task
- Aggiornamento continuo del planning file
- Esecuzione in loop per periodi prolungati

### Layer 5: Monitoring & Logging
- `monitoring.py`: Audit log completo
- Event tracking
- Performance metrics

### Layer 6: API REST
- FastAPI con endpoints per chat, approvals, status
- Integrazione con tutti i layer precedenti

### Layer 7: Containerizzazione
- Dockerfile per produzione
- Docker Compose con PostgreSQL
- Health checks integrati

## Workflow di Implementazione

### Step 1: Inizializzazione
```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate su Windows
pip install -r requirements.txt
```

### Step 2: Configurazione
```bash
cp .env.example .env
# Modifica .env con la chiave Groq
```

### Step 3: Implementazione dei Moduli
1. Copiare `memory.py` dal template
2. Copiare `approval_gate.py` dal template
3. Copiare `monitoring.py` dal template
4. Copiare `task_scheduler.py` dal template

### Step 4: Creazione dell'API
```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/chat")
async def chat(message: str, system_prompt: str = None):
    # Implementazione
    pass

@app.get("/api/status")
async def status():
    # Implementazione
    pass
```

### Step 5: Testing
```bash
python test_nexus.py
```

### Step 6: Deployment
```bash
docker-compose up
# oppure
python START_NEXUS.bat  # Windows
```

## Metriche di Successo

| Metrica | Target | Note |
|---------|--------|------|
| Uptime API | 99.9% | Monitorare con health checks |
| Response time | <500ms | Groq LPU garantisce <200ms |
| Autonomia | 24h+ | Con checkpoint regolari |
| Accuracy | >95% | Dipende dal prompt engineering |
| Test coverage | >80% | Unit + integration test |

## Troubleshooting Comune

### Problema: "GROQ_API_KEY not found"
**Soluzione**: Verificare che `.env` sia configurato correttamente

### Problema: "Port 8000 already in use"
**Soluzione**: Cambiare porta in `.env` (API_PORT=8001)

### Problema: "Memory leak durante autonomia"
**Soluzione**: Implementare garbage collection e checkpoint regolari

### Problema: "Approval Gate timeout"
**Soluzione**: Aumentare timeout o implementare callback asincroni

## Risorse Aggiuntive

- **Groq Console**: https://console.groq.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Docker Docs**: https://docs.docker.com
- **Sanfilippo's Methodology**: Comunicazione empatica con AI
