#!/usr/bin/python3

#basically a 3-level dictionary 
#    {chat_id1 : 
#        {list1 : [item1, item2], 
#        .list1 : [item3, item4], 
#         list2 : [item1, item2],
#        .list2 : [item3] , ...}, 
#     chat_id2
#        {list1 : [item1, item2], 
#        .list1 : [item3, item4], 
#         list2 : [item1, item2],
#        .list2 : [item3] , ...}, 
#..}

import time, os
import pickle
import telepot
import random
import yaml

class Lists(object):
    empty_chat = { 'list':[], 'finished':[] }

    def __init__(self):
        self.listos = {}
        #self.save()

    #save current state to file
    def save():
        f = open('chats/listo')
        f.write(yaml.dump(self.listos))
        f.close()

    #load file state to object
    def load():
        f = open('chats/listo')
        self.listos = yaml.load(f.read())
        f.close()

    #initialized on new chat using the bot
    def new_chat(self, chat_id):
        self.listos[chat_id] = {};

    #create a new list; returns a bool
    def add_listo(self, chat_id, listo):
        if listo not in self.listos[chat_id]:
            self.listos[chat_id][listo]       = []
            self.listos[chat_id]['.' + listo] = []  #completed list
            return True
        else:
            return False

    #add item to existing list; returns a bool
    def add_item(self, chat_id, listo, item):
        if listo in self.listos[chat_id]:
            self.listos[chat_id][listo].append(item)
            return True
        else:
            return False

    #remove item from existing list; returns a bool
    def remove_item(self, chat_id, listo, item):
        if listo in self.listos[chat_id]:
            if item in self.listos[chat_id][listo]:
                self.listos[chat_id][listo].remove(item)
                return True
            else:
                return False
        else:
            return False

    #mark item as completed; returns a bool
    def complete_item(self, chat_id, listo, item):
        if listo in self.listos[chat_id]:
            if item in self.listos[chat_id][listo]:
                self.listos[chat_id][listo].remove(item)
                self.listos[chat_id]['.'+listo].append(item)
                return True
            else:
                return False
        else:
            return False

    #show lists for chat_id; returns a list type
    def list_listos(self, chat_id):
        return self.listos[chat_id].keys()

    #show lists for list_id in a chat_id; returns a list type
    def list_items(self, chat_id, listo):
        if listo in self.listos[chat_id]:
            return self.listos[chat_id][listo]
        else:
            return []

    #return finished lists for list_id and chat_id; returns a list type
    def finished_listos(self, chat_id, listo):
        if listo in self.listos[chat_id]:
            return self.listos[chat_id]['.' + listo]
        else:
            return []



# help info
help_string = "List Bot! A bot for keeping track of lists with your friends and family!. \n\
        /addlist  <list>          Creates a new list \n\
        /list                     Returns current lists \n\
        /list     <list>          List items in a list \n\
        /add      <list> <item>   Add an item to a list \n\
        /rm       <list> <item>   Add an item to a list \n\
        /complete <list> <item>   Mark item as completed \n\
        /finished <list>          List of completed items from a list"


listos = Lists()

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print("got command: {}".format(command))

    #bot.sendMessage(chat_id, "usage: /add <list> <item>")
    #bot.sendMessage(chat_id, "You've watched: \n{}".format(ret))
    #add a listo to the watchlist (creates the group if it didn't exist yet)
    if command[:8] == '/addlist':
        cmd = command.split()
        if len(cmd) < 2:
            bot.sendMessage(chat_id, "usage: /addlist <list>")
        elif listos.add_listo(chat_id, cmd[1]):
            bot.sendMessage(chat_id, "%s added" % cmd[1])
        else:
            bot.sendMessage(chat_id, "%s already exists!" % cmd[1])

    elif command[:4] == '/add':
        cmd = command.split()
        if len(cmd) < 3:
            bot.sendMessage(chat_id, "usage: /add <list> <item>")
        elif listos.add_item(chat_id, cmd[1], cmd[2]):
            bot.sendMessage(chat_id, "%s added to %s" % (cmd[2]. cmd[1]))
        else:
            bot.sendMessage(chat_id, "List %s does not exist" % cmd[1])

    elif command[:5] == '/save':
        telebot.save()

    #elif command[:5] == '/load':
        #telebot.load()

    elif command[:5] == '/list':
        cmd = command.split()
        if len(cmd) < 2:   #just list the lists
            ourlists = listos.list_listos(chat_id)
            if ourlists == []:
                bot.sendMessage(chat_id, "No Lists!")
            else:
                bot.sendMessage(chat_id, "Lists in your group :\n" + '\n'.join(ourlists))
        else:   #list a specific list
            ourlists = listos.list_items(chat_id, listo)
            if ourlists == []:
                bot.sendMessage(chat_id, "Empty or Nonexistent List!\n")
            else:
                bot.sendMessage(chat_id, "Lists in your group : " + '\n'.join(ourlists))



    elif command[:9] == '/finished':
        cmd = command.split()
        if len(cmd) < 2:   #just list the lists
            bot.sendmessage(chat_id, "usage: /finished <list>")
        else:
            ourlist = listo.finished_listos(chat_id, cmd[1])
            bot.sendMessage(chat_id, ("Completed items from %s : " % cmd[1]) + '\n'.join(ourlists))

    elif command[:9] == '/complete':
        cmd = command.split()
        if len(cmd < 3):
            bot.sendMessage(chat_id, "usage: /complete <list> <item>")
        elif listo.complete_item(chat_id, cmd[1], cmd[2]):
            bot.sendMessage(chat_id, "marked %s as completed!" % cmd[2])
        else:
            bot.sendMessage(chat_id, "Error: no such item or list")

    elif command[:3] == '/rm':
        cmd = command.split()
        if len(cmd < 3):
            bot.sendMessage(chat_id, "usage: /rm <list> <item>")
        elif listos.remove_item(chat_id, cmd[1], cmd[2]):
            bot.sendMessage(chat_id, "%s removed from %s" % (cmd[2], cmd[1]))
        else:
            bot.sendMessage(chat_id, "Error: no such item or list")

    # help string
    elif command[:5] == '/help':
        special_str=""
        if random.random() < 0.15:
            special_str += "\nWarning: Do Not Use For Movies!"
        if random.random() < 0.10:
            special_str += "\nNo warantee provided"
        bot.sendMessage(chat_id, help_string + special_str)



f = open('config.yml')
cfgstr = f.read()
mykey = yaml.load(cfgstr)['key']
f.close()
bot = telepot.Bot(mykey)

bot.message_loop(handle)
print("i'm listening yo")

while 1:
    time.sleep(10)
