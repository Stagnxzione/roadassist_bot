from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Optional
import httpx, asyncio, os, json, logging
from telegram.ext import Application, ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

load_dotenv()

# --- Конфиг ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

app = FastAPI()
tickets: Dict[str, dict] = {}

# --- Модель тикета ---
class Ticket(BaseModel):
    incident_type: str
    brand: str
    plate_vats: str
    plate_ref: Optional[str] = None
    location: str
    problem_desc: str
    notes: Optional[str] = None

# --- Jira: создание тикета ---
@app.post("/api/create_ticket")
async def create_ticket(t: Ticket):
    jira_fields = {
        "project": {"key": JIRA_PROJECT_KEY},
        "summary": f"[{t.incident_type}] {t.brand} — {t.plate_vats}",
        "description": f"Местоположение: {t.location}\nОписание: {t.problem_desc}",
        "issuetype": {"name": "Task"},
        "labels": ["ptb", "auto-ticket"],
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
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
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Получить список тикетов ---
@app.get("/api/tickets")
def list_tickets():
    return tickets

# --- Telegram Bot ---
async def run_bot():
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

    async def start(update, context):
        await update.message.reply_text("Привет 👋 Нажми кнопку, чтобы открыть WebApp!")

    tg_app.add_handler(CommandHandler("start", start))

    # Без блокировки event loop
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling()

    # Держим бота запущенным
    await asyncio.Event().wait()

# --- Запуск при старте FastAPI ---
@app.on_event("startup")
async def on_startup():
    if BOT_TOKEN:
        asyncio.create_task(run_bot())
        logging.info("✅ Telegram bot запущен в фоне.")
    else:
        logging.warning("⚠️ BOT_TOKEN не найден. Бот не запущен.")

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend работает"}
