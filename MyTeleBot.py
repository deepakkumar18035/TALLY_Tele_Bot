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

class MyTeleBot:
    def __init__(self,token):
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
            self.updater.bot.setWebhook("https://tally-tele-app.herokuapp.com/"+self.token)
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
        return index
    def rm_row(self,index):
        self.dB = self.dB.drop(index)
        return index
    def get_members(self):
        return " ".join(self.dB.index)
    def clearDB(self):
        self.dB = pd.DataFrame(columns = ["Name","cash","upi","Total"])
        self.dB = self.dB.set_index('Name')