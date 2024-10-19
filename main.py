from flask import Flask, request, Response
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Config
TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_URL = "https://api.telegram.org/bot{token}".format(token=TOKEN)
WEBHOOK_URL  = "https://a903-118-211-29-175.ngrok-free.app"

# bot
app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)

@app.route("/", methods=["POST","GET"])
def index():
  if request.method == "POST":
    msg = request.get_json()
    print("Message received: ", msg)
      
    # trying to parse the message
    # try:
    print("there is a text")
    chat_id = msg['message']['chat']['id']
    text = msg['message']['text'] # gets the text from the message
    
    if text == "options":
      keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes'),
        InlineKeyboardButton("No", callback_data='no')]
      ]
      reply_markup = InlineKeyboardMarkup(keyboard)
      url = f"{TELEGRAM_URL}/sendMessage"
      payload = {
        'chat_id': chat_id,
        'text': "Yes, I am a bot. Do you like talking to bots?",
        'reply_markup': reply_markup.to_dict()
      }
          
      r = requests.post(url, json=payload)
      # Use asyncio.run to await the coroutine
      asyncio.run(bot.send_message(
          chat_id=chat_id,
          text="Yes, I am a bot. Do you like talking to bots?",
          reply_markup=reply_markup
      ))
      
    if text == "are you a bot":
      
      url = "{telegram_url}/sendMessage".format(telegram_url=TELEGRAM_URL)
      payload = {
        'chat_id': chat_id,
        'text': "yes, i am a bot"
      }
    
      # bot.send_message(chat_id=chat_id, text="yes, i am a bot")
      r = requests.post(url, json=payload)
      # asyncio.run(bot.send_message(
      #     chat_id=chat_id,
      #     text="Yes, I am a bot.",
      # ))
          
      if r.status_code == 200:
        return Response('ok', status=200)
      else: 
        return Response('Failed to send message to Telegram', status=500)
    # except:
    #   print("No text found")

    return Response('ok', status=200)

@app.route("/setwebhook", methods=["GET", "POST"])
def setwebhook():
  print("setting webhook")
  s = requests.get("{telegram_url}/setWebhook?url={webhook_url}".format(telegram_url=TELEGRAM_URL,webhook_url=WEBHOOK_URL))

  if s:
    return "Webhook set successfully", 200
  else:
    return "Failed to set webhook", 500

if __name__ == "__main__":
  app.run(debug=True)
