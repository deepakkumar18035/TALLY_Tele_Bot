from MyTeleBot import (
    MyTeleBot,
    ConvHandler,
    DataBase,
    update_excel,
    tableize
    )
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ConversationHandler,
)
import os 
import pandas as pd

os.system("cls")
db = DataBase()
BotId = os.environ.get("BotId")
bot = MyTeleBot(BotId,webhookurl ="https://tally-tele-app.herokuapp.com/")

@bot.add_err_handler()
def error(update, context):
    print(f"Update {update} caused error {context.error}")
@bot.add_command_handler("start")
def start(update, context):
    features = ["rovo","creditcard"]
    features = ["/" + x for x in features]
    update.message.reply_text("\n".join(features))


conversation1 = ConvHandler()
@conversation1.add_entry_handler("CMD","creditcard")
@conversation1.add_state_handler(1,"CBQ","^mainMenu$")
def credit_card_Start_Menu(update,context):
    keyboard = [[InlineKeyboardButton("Add payment", callback_data="add")],
                [InlineKeyboardButton("summary", callback_data="summary"),
                InlineKeyboardButton("cancel", callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message :
        update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    if update.callback_query: 
        query = update.callback_query
        query.answer()
        query.edit_message_text("Select the options below:", reply_markup=reply_markup)
    return 2
@conversation1.add_state_handler(2,"CBQ","^add$|^summary$|^cancel$")
def state2(update,context):
    query = update.callback_query
    if query.data == "add":
        query.answer()
        query.edit_message_text(text="Enter Description:")
        return 3
    if query.data == "summary":
        query.answer("This functionality is currently disabled!")
        summary = ""
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(summary + "\n\n" + "Select the options below:", reply_markup=reply_markup)
        return 1
    if query.data == "cancel":
        query.answer()
        query.edit_message_text("Bye! I hope we can talk again some day.")
        return ConversationHandler.END

@conversation1.add_state_handler(3,"MSG",".*")
def add_payment(update,context):
    conversation1.tracker.append(update.message.text)
    keyboard = [[InlineKeyboardButton("Payment", callback_data="@Payment"),
                InlineKeyboardButton("Transaction", callback_data="@Transaction")],
                [InlineKeyboardButton("Fee", callback_data="@Fee"),
                InlineKeyboardButton("EMI", callback_data="@EMI")],
                [InlineKeyboardButton("Intrest", callback_data="@Intrest")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the Type of transaction:", reply_markup=reply_markup)
    return 4
@conversation1.add_state_handler(4,"CBQ","^@")
def get_payment_amount(update,context):
    query = update.callback_query
    query.answer()
    conversation1.tracker.append(query.data[1:])
    query.edit_message_text("Enter the amount:")
    return 5
@conversation1.add_state_handler(5,"MSG","[0-999]|^-[0-999]")
def payment_update(update,context):
    conversation1.tracker.append(update.message.text)
    latestOutstanding = update_excel(conversation1.tracker[0],conversation1.tracker[2],conversation1.tracker[1])
    update.message.reply_text(conversation1.tracker[2] + " paid for " + conversation1.tracker[0] + " - " + conversation1.tracker[1] + ". \n" +
        "Your Current Outstanding = " + latestOutstanding)
    conversation1.tracker = []
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    return 1

@conversation1.add_fallback_handler("CMD","cancel")
def conversation1_cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END
bot.add_convo_handler(conversation1.get_handler())

conversation2 = ConvHandler()
@conversation2.add_entry_handler("CMD","rovo")
@conversation2.add_state_handler(1,"CBQ","^mainMenu$")
def ROVO_Start_Menu(update,context):
    keyboard = [[InlineKeyboardButton("add", callback_data="add"),
                InlineKeyboardButton("remove", callback_data="remove"),
                InlineKeyboardButton("edit APP", callback_data="edit_APP")],
                [InlineKeyboardButton("table", callback_data="table"),
                InlineKeyboardButton("clear", callback_data="clear"),
                InlineKeyboardButton("cancel", callback_data="cancel")],
                [InlineKeyboardButton("summary", callback_data="summary"),
                InlineKeyboardButton("paid", callback_data="paid")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message :
        update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    if update.callback_query: 
        query = update.callback_query
        query.answer()
        query.edit_message_text("Select the options below:", reply_markup=reply_markup)
    return 2
@conversation2.add_state_handler(2,"CBQ","^add$|^remove$|^summary$|^clear$|^paid$|^cancel$|^edit_APP$|^table$")
def state2(update,context):
    query = update.callback_query
    if query.data == "add":
        query.answer()
        query.edit_message_text(text="Enter names to add:")
        return 3
    query = update.callback_query
    if query.data == "edit_APP":
        query.answer()
        query.edit_message_text(text="Enter amount per person:")
        return 6
    if query.data == "remove":
        query.answer()
        n = 3
        keyboard = [InlineKeyboardButton(x, callback_data="@"+x) for x in db.dB.index]
        keyboard = [keyboard[i:i+n] for i in range(0, len(keyboard), n)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Select names to remove:", reply_markup=reply_markup)
        return 3
    if query.data == "summary":
        query.answer()
        summary = db.makeSumamry()
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(summary + "\n\n" + "Select the options below:", reply_markup=reply_markup)
        return 1
    if query.data == "table":
        query.answer()
        summary = db.showtable()
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(summary + "\n" + "Select the options below:", reply_markup=reply_markup)
        return 1
    if query.data == "clear":
        db.clearDB()
        query.answer("Database cleared!")
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Select the options below:", reply_markup=reply_markup)
        return 1
    if query.data == "cancel":
        query.answer()
        query.edit_message_text("Bye! I hope we can talk again some day.")
        return ConversationHandler.END
    if query.data == "paid":
        query.answer()
        n = 3
        keyboard = [InlineKeyboardButton(x, callback_data="@"+x) for x in db.dB.index]
        keyboard = [keyboard[i:i+n] for i in range(0, len(keyboard), n)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Who?", reply_markup=reply_markup)
        return 4

@conversation2.add_state_handler(3,"MSG",".*")
def add_members(update,context):
    members = [db.add_empty_row(y) for y in update.message.text.replace('\n', '-').split("-")]
    update.message.reply_text(", ".join(members) + " added!")
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    return 1
@conversation2.add_state_handler(3,"CBQ","^@")
def rmv_members(update,context):
    query = update.callback_query
    query.answer()
    db.rm_row(query.data[1:])
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(query.data[1:] + " removed!\nSelect the options below:", reply_markup=reply_markup)
    return 1
@conversation2.add_state_handler(4,"CBQ","^@|^cash$|^upi$")
def payment_options(update,context):
    query = update.callback_query
    query.answer()
    if query.data not in ["cash","upi"]:
        conversation2.tracker.append(query.data[1:])
        keyboard = [[InlineKeyboardButton("Cash", callback_data="cash"),
                    InlineKeyboardButton("UPI", callback_data="upi")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("How?", reply_markup=reply_markup)
        return 4
    else:
        conversation2.tracker.append(query.data)
        query.edit_message_text(text="Enter amount:")
        return 5
@conversation2.add_state_handler(5,"MSG","[0-999]|^-[0-999]")
def payment_update(update,context):
    conversation2.tracker.append(update.message.text)
    db.dB.loc[conversation2.tracker[0]][conversation2.tracker[1]] = int(conversation2.tracker[2])
    update.message.reply_text(conversation2.tracker[0] + " paid " + conversation2.tracker[2] + " by " + conversation2.tracker[1])
    conversation2.tracker = []
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    return 1
@conversation2.add_state_handler(6,"MSG","[0-999]|^-[0-999]")
def edit_APP(update,context):
    db.set_app(int(update.message.text))
    update.message.reply_text("Amount per person updated!")
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    return 1

@conversation2.add_fallback_handler("CMD","cancel")
def conversation2_cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END
bot.add_convo_handler(conversation2.get_handler())

db1 = DataBase()
conversation3 = ConvHandler()
@conversation3.add_entry_handler("CMD","roundTable")
def credit_card_Start_Menu(update,context):
    members = [db1.add_empty_row(y) for y in update.message.text.replace('\n', '-').split("-")]
    update.message.reply_text(", ".join(members) + " added!")
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the options below:", reply_markup=reply_markup)
bot.add_convo_handler(conversation3.get_handler())

print("Tally is online now.\n")
#bot.run("polling")
bot.run("webhook")

