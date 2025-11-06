from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
import httpx, asyncio, os, json
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

app = FastAPI()
tickets: Dict[str, dict] = {}

class Ticket(BaseModel):
    incident_type: str
    brand: str
    plate_vats: str
    plate_ref: str | None = None
    location: str
    problem_desc: str
    notes: str | None = None

@app.post("/api/create_ticket")
async def create_ticket(t: Ticket):
    jira_fields = {
        "project": {"key": JIRA_PROJECT_KEY},
        "summary": f"[{t.incident_type}] {t.brand} — {t.plate_vats}",
        "description": f"Местоположение: {t.location}\nОписание: {t.problem_desc}",
        "issuetype": {"name": "Task"},
        "labels": ["ptb", "auto-ticket"],
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{JIRA_BASE_URL}/rest/api/3/issue",
            json={"fields": jira_fields},
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        )
        if r.status_code == 201:
            data = r.json()
            key = data.get("key")
            tickets[key] = t.dict()
            return {"success": True, "jira_key": key}
        else:
            return {"success": False, "error": r.text}

@app.get("/api/tickets")
def list_tickets():
    return tickets

async def run_bot():
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

    async def start(update, context):
        await update.message.reply_text("Привет 👋 Нажми кнопку, чтобы открыть WebApp!")

    tg_app.add_handler(CommandHandler("start", start))
    await tg_app.run_polling()

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(run_bot())

@app.get("/")
def home():
    return {"status": "Backend working"}
