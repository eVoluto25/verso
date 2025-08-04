# main.py
from prompt_coach import PROMPT_COACH
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Literal
from supabase import create_client, Client
import os
import datetime

# --- Configurazione Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE_NAME = os.environ.get("SUPABASE_TABLE_NAME_V") 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Init App ---
app = FastAPI()

# --- Schema delle risposte multiple choice ---
class RisposteOnboarding(BaseModel):
    fascia_eta: Literal['A', 'B', 'C', 'D', 'E']
    genere: Literal['A', 'B', 'C']
    obiettivo: Literal['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    livello: Literal['A', 'B', 'C']
    giorni_sett: Literal['A', 'B', 'C', 'D']
    attrezzatura: Literal['A', 'B', 'C', 'D']
    infortuni: Literal['A', 'B']
    alimentazione: Literal['A', 'B']

# --- Endpoint per ricevere e salvare le risposte ---
@app.post("/onboarding")
async def salva_risposte(risposte: RisposteOnboarding):
    try:
        data = risposte.dict()
        data["created_at"] = datetime.datetime.utcnow().isoformat()

        # Salva su Supabase
        response = supabase.table(SUPABASE_TABLE_NAME_V).insert(data).execute()
        
        # Restituisci prompt operativo al GPT
        return JSONResponse(content={"prompt_operativo": PROMPT_COACH}, status_code=200)


        if response.get("status_code") == 201:
            return {"status": "ok"}
        else:
            return {"status": "errore", "dettaglio": response}

    except Exception as e:
        return {"status": "errore", "dettaglio": str(e)}
