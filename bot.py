import asyncio
import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define states
CATEGORY, ADD_PAYMENT = range(2)

# Define category options
CATEGORIES = ['Utilities', 'Subscriptions', 'Fitness', 'Other']

# Define a start command
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info(f"User {user.id} started the conversation")

    keyboard = [
      [InlineKeyboardButton(category, callback_data=category) for category in CATEGORIES[:2]],
      [InlineKeyboardButton(category, callback_data=category) for category in CATEGORIES[2:]]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Welcome to Collie! 👋 \n\n" 
        "I'm here to help you consolidate and manage your monthly payments, "
        "including bills and entertainment subscriptions. 📅💰\n\n"
        "Let's start by identifying the categories of payments you want to manage. "
        "Please type the categories (e.g., utilities, entertainment, subscriptions).",
        reply_markup=reply_markup
    )
    return CATEGORY

async def category(update: Update, context: CallbackContext) -> None:
    logger.info(f"Category callback query received")

    query = update.callback_query
    await query.answer() # answering callback query (must)

    selected_category = query.data
    logger.info(f"selected category: {selected_category}")

    # return ADD_PAYMENT

async def cancel(update: Update, context: CallbackContext) -> int:
  """Cancels and ends the conversation."""
  await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
  return ConversationHandler.END

# Define a help command
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('You can ask me anything!')
    
async def setup_application() -> None:
  bot_token = os.getenv('BOT_TOKEN')
  if not bot_token:
    raise ValueError("BOT_TOKEN not set in environment variables")

  application = Application.builder().token(bot_token).build()  
  
  conv_handler = ConversationHandler(
      entry_points=[CommandHandler("start", start)],
      states={
          CATEGORY: [CallbackQueryHandler(category, pattern='^' + '|'.join(CATEGORIES) + '$')]
          # ADD_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_payment)],
      },
      fallbacks=[CommandHandler('cancel', cancel)],
    )

  application.add_handler(conv_handler)
  return application

def webhook(request):
  async def process_update():
    application = await setup_application()
    await application.initialize()
    await application.process_update(
      Update.de_json(request.get_json(force=True), application.bot)
    )
  
  if request.method == 'POST':
    asyncio.run(process_update())

  return 'ok'

# # Main function to set up the bot
# def main() -> None:
#     # Create an application and pass in the bot's token
#     application = Application.builder().token(TOKEN).build()

#     conv_handler = ConversationHandler(
#       entry_points=[CommandHandler("start", start)],
#       states={
#           CATEGORY: [CallbackQueryHandler(category, pattern='^' + '|'.join(CATEGORIES) + '$')]
#           # ADD_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_payment)],
#       },
#       fallbacks=[CommandHandler('cancel', cancel)],
#     )

#     application.add_handler(conv_handler)

#     # application.add_handler(CommandHandler("start", start))
#     # application.add_handler(CommandHandler("help", help_command))

#     # # Run the bot until you press Ctrl-C
#     application.run_polling()

if __name__ == '__main__':
    main()
