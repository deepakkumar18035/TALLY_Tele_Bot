from MyTeleBot import MyTeleBot,ConvHandler,DataBase
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ConversationHandler,
)
import os 
import pandas as pd

def tableize(df):
    if not isinstance(df, pd.DataFrame):
        return
    df_columns = df.columns.tolist() 
    max_len_in_lst = lambda lst: len(sorted(lst, reverse=True, key=len)[0])
    align_center = lambda st, sz: "{0}{1}{0}".format(" "*(1+(sz-len(st))//2), st)[:sz] if len(st) < sz else st
    align_right = lambda st, sz: "{0}{1} ".format(" "*(sz-len(st)-1), st) if len(st) < sz else st
    max_col_len = max_len_in_lst(df_columns)
    max_val_len_for_col = dict([(col, max_len_in_lst(df.iloc[:,idx].astype('str'))) for idx, col in enumerate(df_columns)])
    col_sizes = dict([(col, 2 + max(max_val_len_for_col.get(col, 0), max_col_len)) for col in df_columns])
    build_hline = lambda row: '+'.join(['-' * col_sizes[col] for col in row]).join(['+', '+'])
    build_data = lambda row, align: "|".join([align(str(val), col_sizes[df_columns[idx]]) for idx, val in enumerate(row)]).join(['|', '|'])
    hline = build_hline(df_columns)
    out = [hline, build_data(df_columns, align_center), hline]
    for _, row in df.iterrows():
        out.append(build_data(row.tolist(), align_right))
    out.append(hline)
    return "\n".join(out)

os.system("cls")
db = DataBase()
#BotId = os.environ.get("BotId")
BotId = "5207952198:AAEGoOTJeQCCQ0aufZLrIIn0O4UFaahYit0"
bot = MyTeleBot(BotId,webhookurl ="https://tally-tele-app.herokuapp.com/")

@bot.add_err_handler()
def error(update, context):
    print(f"Update {update} caused error {context.error}")

conversation2 = ConvHandler()
@conversation2.add_entry_handler("CMD","rovo")
@conversation2.add_state_handler(1,"CBQ","^mainMenu$")
def ROVO_Start_Menu(update,context):
    keyboard = [[InlineKeyboardButton("add", callback_data="add"),
                InlineKeyboardButton("remove", callback_data="remove"),
                InlineKeyboardButton("paid", callback_data="paid")],
                [InlineKeyboardButton("summary", callback_data="summary"),
                InlineKeyboardButton("clear", callback_data="clear"),
                InlineKeyboardButton("cancel", callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message :
        update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    if update.callback_query: 
        query = update.callback_query
        query.answer()
        query.edit_message_text("Select the options below:", reply_markup=reply_markup)
    return 2
@conversation2.add_state_handler(2,"CBQ","^add$|^remove$|^summary$|^clear$|^paid$|^cancel$")
def state2(update,context):
    query = update.callback_query
    if query.data == "add":
        query.answer()
        query.edit_message_text(text="Enter names to add:")
        return 3
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
        x = db.dB.copy(deep=True)
        x["Total"] = x["cash"] + x["upi"]
        x.loc["Total"] = x.sum()
        x['name'] = x.index
        temp = x['name']
        x.drop(labels=['name'], axis=1,inplace = True)
        x.insert(0, 'name', temp)
        summary = tableize(x)
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="mainMenu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(summary + "\n\n" + "Select the options below:", reply_markup=reply_markup)
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

@conversation2.add_fallback_handler("CMD","cancel")
def conversation2_cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END
bot.add_convo_handler(conversation2.get_handler())

bot.run("webhook")
print("Tally is online now.\n")

#updater.start_webhook(listen="0.0.0.0",
#                        port=int(os.environ.get("PORT",3978)),
#                        url_path=BotId)
#updater.bot.setWebhook("https://tally-tele-app.herokuapp.com/"+BotId
