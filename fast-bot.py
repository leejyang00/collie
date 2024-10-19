import logging
from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pyngrok import ngrok
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

# Your bot token from the environment or hardcoded
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN)

# Initialize Application with bot token (python-telegram-bot 20+ uses Application)
application = Application.builder().token(BOT_TOKEN).build()

# Function to set webhook URL dynamically
async def set_webhook(url: str):
    webhook_url = f"{url}/webhook/{BOT_TOKEN}"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Hello! This is your bot!"
    )

# Handle webhook updates (POST requests from Telegram)
@app.post("/webhook/{token}")
async def handle_webhook(token: str, request: Request):
    if token == BOT_TOKEN:
        data = await request.json()
        update = Update.de_json(data, bot)
        await application.process_update(update)
    return {"status": "ok"}

# FastAPI startup event to set webhook automatically when the app starts
@app.on_event("startup")
async def startup_event():
    # Start a tunnel for ngrok and set the webhook URL
    http_tunnel = ngrok.connect(8000)
    public_url = http_tunnel.public_url
    logger.info(f"Ngrok tunnel created: {public_url}")
    
    await set_webhook(public_url)

# Add command handlers to the bot
application.add_handler(CommandHandler("start", start))

# FastAPI root endpoint for health check or testing
@app.get("/")
async def index():
    return {"message": "Bot is running!"}

# Run the app using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
