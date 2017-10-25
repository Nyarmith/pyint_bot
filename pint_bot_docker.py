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

import telepot
import pexpect
import os

#start python interpreter session in expect
session = pexpect.spawn('python3')
session.expect('>>>')

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print("got command: {}".format(command))

    if command[:4] == '/run':
        cmd = command[5:]
        ret = runCmd(cmd)
        session.sendline(cmd)
        session.expect('>>>')
        bot.sendMessage(chat_id, session.before)

    elif command[:5] == '/help':
        special_str="lol"
        bot.sendMessage(chat_id, help_string + special_str)



mykey = os.environ['TELEKEY'] #yaml.load(cfgstr)['key']
bot = telepot.Bot(mykey)

bot.message_loop(handle, run_forever=True)
print("i'm listening yo")
