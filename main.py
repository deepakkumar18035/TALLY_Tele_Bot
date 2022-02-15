from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from telegram import ReplyKeyboardMarkup, ParseMode
import os 
import pandas as pd

BotId = os.environ.get("BotId")
class DataBase:
    def __init__(self):
        self.dB = pd.DataFrame(columns = ["Name","cash","upi","Total"])
        self.dB = self.dB.set_index('Name')
    def add_empty_row(self,index):
        self.dB = self.dB.append(pd.Series({'cash':0,'upi':0},name=index,dtype='int64'))
        return index
    def rm_row(self,index):
        self.dB = self.dB.drop(index)
        return index
    def get_members(self):
        return " ".join(self.dB.index)
    def clearDB(self):
        self.dB = pd.DataFrame(columns = ["Name","cash","upi","Total"])
        self.dB = self.dB.set_index('Name')

db = DataBase()

def start_command(update, context):
    name = update.message.from_user.first_name
    update.message.reply_text("Hey "+str(name)+"!")
    db.clearDB()

def add_command(update, context):
    members = [db.add_empty_row(y) for x in context.args for y in x.split("-")]
    os.system("cls")
    print(db.dB)
    update.message.reply_text(" ".join(members) + " added.")

def rm_command(update, context):
    members = [db.rm_row(y) for x in context.args for y in x.split("-")]
    os.system("cls")
    print(db.dB)
    update.message.reply_text(" ".join(members) + " removed.")

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

def sumamry_command(update, context):
    x = db.dB.copy(deep=True)
    x["Total"] = x["cash"] + x["upi"]
    x.loc["Total"] = x.sum()
    x['name'] = x.index
    temp = x['name']
    x.drop(labels=['name'], axis=1,inplace = True)
    x.insert(0, 'name', temp)
    update.message.reply_text(tableize(x))

def help_command(update, context):
    update.message.reply_text("/start \n /add \n /remove\n /summary \n /paid \n /help")

def handle_message(update, context):
    name = update.message.from_user.first_name
    """
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
    """
    update.message.reply_text("This project is under developement. You don't have privilege to access it now.")

def error(update, context):
    print(f"Update {update} caused error {context.error}")


nameState, typeState, amountState = range(3)
CurrentPos = []
def paid_command(update, context):
    keys = []
    for x in db.dB.index:
        keys.append(["@"+x])
    reply_markup = ReplyKeyboardMarkup(keys,one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("Who?",reply_markup=reply_markup)
    return nameState
def typeValue(update,context): 
    CurrentPos.append(update.message.text[1:])   
    keys = [["cash","upi"]]
    reply_markup = ReplyKeyboardMarkup(keys,one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("How?",reply_markup=reply_markup)
    return typeState
def amountValue(update,context):
    CurrentPos.append(update.message.text)      
    update.message.reply_text("Enter the amount:")
    return amountState
def updateValue(update,context): 
    global CurrentPos
    CurrentPos.append(update.message.text)   
    print(CurrentPos)
    db.dB.loc[CurrentPos[0]][CurrentPos[1]] = int(CurrentPos[2])
    CurrentPos = []
    update.message.reply_text("Added")
    return ConversationHandler.END
def cancel(update, context):
    global CurrentPos
    user = update.message.from_user
    update.message.reply_text('Bye! I hope we can talk again some day.')
    CurrentPos = []
    return ConversationHandler.END

os.system("cls")
print("Tally is online now.\n")
updater = Updater(BotId, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start",start_command))
dispatcher.add_handler(CommandHandler("help",help_command))
dispatcher.add_handler(CommandHandler("add",add_command))
dispatcher.add_handler(CommandHandler("remove",rm_command))
dispatcher.add_handler(CommandHandler("summary",sumamry_command))
dispatcher.add_handler(CommandHandler("clear",cancel))
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('paid', paid_command)],
    states={
        nameState: [MessageHandler(Filters.regex('^@'), typeValue)],
        typeState: [MessageHandler(Filters.regex('^cash$') | Filters.regex('^upi$'), amountValue)],
        amountState: [ MessageHandler(Filters.regex('[0-999]') | Filters.regex('^-[0-999]'), updateValue)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)
dispatcher.add_error_handler(error)
#updater.start_polling()
updater.start_webhook(listen="0.0.0.0",
                        port=os.environ.get("PORT",443),
                        url_path=BotId,
                        webhook_url="https://tally-tele-app.herokuapp.com/"+BotId)
updater.idle()
