async def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} started the conversation.")
    
    keyboard = [
        [InlineKeyboardButton(category, callback_data=category) for category in CATEGORIES[:2]],
        [InlineKeyboardButton(category, callback_data=category) for category in CATEGORIES[2:]]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Hi {user.first_name}, welcome to Collie! 👋\n\n"
        "I'm here to help you consolidate and manage your monthly payments, "
        "including bills and entertainment subscriptions. 📅💰\n\n"
        "Please select a category of payments you want to manage:",
        reply_markup=reply_markup
    )
    return CATEGORY

async def category(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    
    selected_category = query.data
    user = query.from_user
    logger.info(f"User {user.id} selected category: {selected_category}")
    
    context.user_data['current_category'] = selected_category
    
    await query.edit_message_text(
        f"You selected: {selected_category}\n"
        f"Now, please provide the service name, amount, and due date for a {selected_category} payment.\n"
        "For example: Netflix, $15, 15th of each month."
    )
    return DETAILS

async def details(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    if 'details' not in context.user_data:
        context.user_data['details'] = {}
    
    current_category = context.user_data['current_category']
    if current_category not in context.user_data['details']:
        context.user_data['details'][current_category] = []
    
    payment_details = update.message.text
    context.user_data['details'][current_category].append(payment_details)
    logger.info(f"User {user.id} added payment details for {current_category}: {payment_details}")
    
    keyboard = [
        [InlineKeyboardButton("Add another payment", callback_data="add_more")],
        [InlineKeyboardButton("Choose a different category", callback_data="new_category")],
        [InlineKeyboardButton("Finish", callback_data="finish")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Got it! What would you like to do next?",
        reply_markup=reply_markup
    )
    return CATEGORY

async def cancel(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} canceled the conversation.")
    await update.message.reply_text('Bye! Hope to talk to you again soon.')
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CATEGORY: [
                CallbackQueryHandler(category, pattern='^' + '|'.join(CATEGORIES) + '$'),
                CallbackQueryHandler(start, pattern='^new_category$'),
                CallbackQueryHandler(cancel, pattern='^finish$')
            ],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, details)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    
    logger.info("Bot started")
    application.run_polling()

if __name__ == '__main__':
    main()
