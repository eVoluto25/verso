# main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Literal
from supabase import create_client, Client
import os
import datetime
import logging
from mental_prompt import mental_prompt

# --- Logger ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verso")

# --- Prompt da modulo esterno ---
from prompt_coach import prompt_operativo

# --- Configurazione Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE_NAME_V = os.getenv("SUPABASE_TABLE_NAME_V")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Init App ---
app = FastAPI()

# --- Schema delle risposte multiple choice ---
class RisposteOnboarding(BaseModel):
    fascia_eta: str
    genere: str
    obiettivo: str
    livello: str
    giorni_sett: str
    attrezzatura: str
    infortuni: str
    alimentazione: str
    corporatura: str
    
class MentalInput(BaseModel):
    messaggio: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("*", mode="before")
    @classmethod
    def uppercase_fields(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("*")
    @classmethod
    def validate_value(cls, v, info):
        validi = {
            "fascia_eta": ['A', 'B', 'C', 'D', 'E'],
            "genere": ['A', 'B', 'C'],
            "obiettivo": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
            "livello": ['A', 'B', 'C'],
            "giorni_sett": ['A', 'B', 'C', 'D'],
            "attrezzatura": ['A', 'B', 'C', 'D'],
            "infortuni": ['A', 'B'],
            "alimentazione": ['A', 'B'],
            "corporatura": ['A', 'B', 'C', 'D', 'E', 'F'],
             "messaggio": ["A", "B"],
        }
        field_name = info.field_name
        if v not in validi[field_name]:
            raise ValueError(f"Valore non valido per {field_name}: {v}")
        return v

@app.get("/")
def root():
    return {"status": "online"}

@app.post("/mental_reset")
async def mental_reset(data: MentalInput):
    try:
        if not data.messaggio:
            raise ValueError("Campo 'messaggio' mancante o vuoto")
        
        logger.info(f"[MIND UNDER PRESSURE] Richiesta ricevuta: {data.messaggio}")
        logger.info("[MIND UNDER PRESSURE] Prompt mentale inviato con successo.")
        return JSONResponse(
            status_code=200,
            content={"prompt_mentale": mental_prompt.strip()}
        )
    except Exception as e:
        logger.error(f"[MIND UNDER PRESSURE] Errore: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"errore": "Errore mental_reset", "dettaglio": str(e)}
        )

# --- Endpoint per ricevere e salvare le risposte ---
@app.post("/onboarding")
async def salva_risposte(risposte: RisposteOnboarding):
    try:
        data = risposte.dict()
        data["created_at"] = datetime.datetime.utcnow().isoformat()
        logger.info(f"Ricevute risposte: {data}")

        response = supabase.table(SUPABASE_TABLE_NAME_V).insert(data).execute()
        logger.info(f"Risposta Supabase: {response}")

        return JSONResponse(
            status_code=200,
            content={"prompt_operativo": prompt_operativo.strip()}
        )
    except Exception as e:
        logger.error(f"Errore durante il salvataggio: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"errore": "Errore imprevisto", "dettaglio": str(e)}
        )
