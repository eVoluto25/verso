# main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Literal
from supabase import create_client, Client
import os
import datetime

# --- Configurazione Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
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

        # Inserisce nella tabella Supabase
        response = supabase.table("coach_onboarding").insert(data).execute()

        if response.get("status_code") == 201:
            return {"status": "ok"}
        else:
            return {"status": "errore", "dettaglio": response}

    except Exception as e:
        return {"status": "errore", "dettaglio": str(e)}
