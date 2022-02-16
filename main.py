from MyTeleBot import MyTeleBot,ConvHandler,DataBase
from telegram import ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
)
import os 
import pandas as pd


os.system("cls")
#BotId = os.environ.get("BotId")
BotId = "5207952198:AAEGoOTJeQCCQ0aufZLrIIn0O4UFaahYit0"
db = DataBase()

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



bot = MyTeleBot("5207952198:AAEGoOTJeQCCQ0aufZLrIIn0O4UFaahYit0")

@bot.add_command_handler("start")
def start_command(update, context):
    name = update.message.from_user.first_name
    update.message.reply_text("Hey "+str(name)+"!")
    db.clearDB()

@bot.add_command_handler("help")
def help_command(update, context):
    update.message.reply_text("/start \n /add \n /remove\n /summary \n /paid \n /help")

@bot.add_command_handler("add")
def add_command(update, context):
    members = [db.add_empty_row(y) for x in context.args for y in x.split("-")]
    os.system("cls")
    print(db.dB)
    update.message.reply_text(" ".join(members) + " added.")

@bot.add_command_handler("remove")
def rm_command(update, context):
    members = [db.rm_row(y) for x in context.args for y in x.split("-")]
    os.system("cls")
    print(db.dB)
    update.message.reply_text(" ".join(members) + " removed.")

@bot.add_command_handler("summary")
def sumamry_command(update, context):
    x = db.dB.copy(deep=True)
    x["Total"] = x["cash"] + x["upi"]
    x.loc["Total"] = x.sum()
    x['name'] = x.index
    temp = x['name']
    x.drop(labels=['name'], axis=1,inplace = True)
    x.insert(0, 'name', temp)
    update.message.reply_text(tableize(x))

"""
@bot.add_msg_handler(".*")
def handle_message(update, context):
    name = update.message.from_user.first_name
    #if name in ["Deepak Kumar","Harish"]:
    #    text = str(update.message.text).lower()
    #    print("\nReceived Script: " + text + "\n")
    #    status = R.develope(update.message.chat.id,text)
    #    if status:
    #        sentStatus = R.send_file(update.message.chat.id)
    #        print(["Video sent Sucessfully!" if sentStatus else "Unable to upload Video files."][0])
    #    else:
    #        update.message.reply_text(str("Something unexpected happen! Please try again later."))
    #else:
    #    update.message.reply_text("This project is under developement. You don't have privilege to access it now.")
    update.message.reply_text("This project is under developement. You don't have privilege to access it now.")
"""

@bot.add_err_handler()
def error(update, context):
    print(f"Update {update} caused error {context.error}")

"""
conversation1 = ConvHandler()
conversation1.tracker = []
@conversation1.add_entry_handler("CMD","paid")
def paid_command(update, context):
    keys = []
    for x in db.dB.index:
        keys.append(["@"+x])
    reply_markup = ReplyKeyboardMarkup(keys,one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("Who?",reply_markup=reply_markup)
    return 1
@conversation1.add_state_handler(1,"MSG","^@")
def typeValue(update,context): 
    conversation1.tracker.append(update.message.text[1:])   
    keys = [["cash","upi"]]
    reply_markup = ReplyKeyboardMarkup(keys,one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("How?",reply_markup=reply_markup)
    return 2
@conversation1.add_state_handler(2,"MSG","^cash$|^upi$")
def amountValue(update,context):
    conversation1.tracker.append(update.message.text)      
    update.message.reply_text("Enter the amount:")
    return 3
@conversation1.add_state_handler(3,"MSG","[0-999]|^-[0-999]")
def updateValue(update,context): 
    conversation1.tracker.append(update.message.text)   
    print(conversation1.tracker)
    db.dB.loc[conversation1.tracker[0]][conversation1.tracker[1]] = int(conversation1.tracker[2])
    conversation1.tracker = []
    update.message.reply_text("Added")
    return ConversationHandler.END
@conversation1.add_fallback_handler("CMD","cancel")
def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.')
    conversation1.tracker = []
    return ConversationHandler.END
bot.add_convo_handler(conversation1.get_handler())
"""

conversation2 = ConvHandler()
@conversation2.add_entry_handler("CMD","rovo")
def ROVO_Start_Menu(update,context):
    keyboard = [[InlineKeyboardButton("add", callback_data="add"),
                InlineKeyboardButton("remove", callback_data="remove"),
                InlineKeyboardButton("summary", callback_data="summary"),
                InlineKeyboardButton("clear", callback_data="clear")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the options below:", reply_markup=reply_markup)
    return 1
@conversation2.add_state_handler(1,"CBQ","^add$|^remove$|^summary$|^clear$|^paid$")
def state1(update,context):
    query = update.callback_query
    query.answer()
    keyboard = [[]]
    if query.data == "add":
        


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
    return ConversationHandler.END
@conversation2.add_fallback_handler("CMD","cancel")
def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END
bot.add_convo_handler(conversation2.get_handler())


print("Tally is online now.\n")
bot.run("polling")

#updater.start_webhook(listen="0.0.0.0",
#                        port=int(os.environ.get("PORT",3978)),
#                        url_path=BotId)
#updater.bot.setWebhook("https://tally-tele-app.herokuapp.com/"+BotId
