from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)
import os
import pandas as pd
import requests

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

def update_excel(desc,amount,type):
    url = 'https://script.google.com/macros/s/AKfycby8GtcbWz_x06tbhYVQlDa-Ml4eTkXiFYvOBQCxO_yNVeYp4e9z/exec'
    myobj = {'action': 'addCreditCardTransaction',
                "description":desc,
                "amount":amount,
                "category":type
            }
    x = requests.post(url, data = myobj)
    print(x.text)

class MyTeleBot:
    def __init__(self,token,webhookurl=None):
        self.webhookurl = webhookurl
        self.token = token
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
    def run(self,type):
        if type == "polling":
            self.updater.start_polling()
        else:
            self.updater.start_webhook(listen="0.0.0.0",
                                    port=int(os.environ.get("PORT",3978)),
                                    url_path=self.token)
            if self.webhookurl == None:
                raise Exception("Webhook Url not provided.")
            else:
                self.updater.bot.setWebhook(self.webhookurl + self.token)
        self.updater.idle()
    def add_command_handler(self,cmnd):
        def decorator(cmndFunc):
            self.dispatcher.add_handler(CommandHandler(cmnd,cmndFunc))
            return cmndFunc
        return decorator
    def add_msg_handler(self,regexPattern):
        def decorator(msgFunc):
            self.dispatcher.add_handler(MessageHandler(Filters.regex(regexPattern),msgFunc))
            return msgFunc
        return decorator
    def add_err_handler(self):
        def decorator(msgFunc):
            self.dispatcher.add_error_handler(msgFunc)
            return msgFunc
        return decorator
    def add_convo_handler(self,convo):
        self.dispatcher.add_handler(convo)
        return


class ConvHandler:
    def __init__(self):
        self.entry_points = []
        self.fallbacks = []
        self.states = {}
        self.tracker = []
    def add_entry_handler(self,handlerType,textPattern):
        def decorator(func):
            if handlerType == "CMD":
                handler = CommandHandler(textPattern,func)
            if handlerType == "MSG":
                handler = MessageHandler(Filters.regex(textPattern),func)
            if handlerType == "CBQ":
                handler = CallbackQueryHandler(func,pattern=textPattern)
            self.entry_points.append(handler)
            return func
        return decorator
    def add_fallback_handler(self,handlerType,textPattern):
        def decorator(func):
            if handlerType == "CMD":
                handler = CommandHandler(textPattern,func)
            if handlerType == "MSG":
                handler = MessageHandler(Filters.regex(textPattern),func)
            if handlerType == "CBQ":
                handler = CallbackQueryHandler(func,pattern=textPattern)
            self.fallbacks.append(handler)
            return func
        return decorator
    def add_state_handler(self,state,handlerType,textPattern):
        def decorator(func):
            if handlerType == "CMD":
                handler = CommandHandler(textPattern,func)
            if handlerType == "MSG":
                handler = MessageHandler(Filters.regex(textPattern),func)
            if handlerType == "CBQ":
                handler = CallbackQueryHandler(func,pattern=textPattern)
            if state in self.states:
                self.states[state].append(handler)
            else:
                self.states[state] = [handler]
            return func
        return decorator
    def get_handler(self):
        return ConversationHandler(entry_points = self.entry_points,states=self.states,fallbacks=self.fallbacks)

class DataBase:
    def __init__(self):
        self.dB = pd.DataFrame(columns = ["Name","cash","upi","Total"])
        self.dB = self.dB.set_index('Name')
    def add_empty_row(self,index):
        self.dB = self.dB.append(pd.Series({'cash':0,'upi':0},name=index,dtype='int64'))
        os.system("cls")
        print(self.dB)
        return index
    def rm_row(self,index):
        self.dB = self.dB.drop(index)
        os.system("cls")
        print(self.dB)
        return index
    def get_members(self):
        return " ".join(self.dB.index)
    def clearDB(self):
        self.dB = pd.DataFrame(columns = ["Name","cash","upi","Total"])
        self.dB = self.dB.set_index('Name')