import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
    MessageHandler,Filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)

def paid(update, context):
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    members = ["x","y","z"]
    keyboard = [[]]
    for x in members:
        keyboard[0].append(InlineKeyboardButton(x, callback_data="@"+x))
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Who?", reply_markup=reply_markup)
    return FIRST
def payType(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Cash", callback_data="cash"),
            InlineKeyboardButton("UPI", callback_data="upi"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Payment Type", reply_markup=reply_markup
    )
    return FIRST
def amount(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("75", callback_data=str(THREE)),
            InlineKeyboardButton("90", callback_data=str(FOUR)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Enter amount:")
    return SECOND
def ack(update,context): 
    update.message.reply_text("Added")
    return ConversationHandler.END
def cancel(update,context): 
    update.message.reply_text("Cancelled")
    return ConversationHandler.END
def main() -> None:
    updater = Updater("5207952198:AAEGoOTJeQCCQ0aufZLrIIn0O4UFaahYit0")
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('paid', paid)],
        states={
            FIRST: [
                CallbackQueryHandler(payType, pattern='^@'),
                CallbackQueryHandler(amount, pattern='^cash$|^upi$'),
            ],
            SECOND: [MessageHandler(Filters.regex('[0-999]') | Filters.regex('^-[0-999]'), ack)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()