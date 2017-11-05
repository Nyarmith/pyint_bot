#!/usr/bin/python3
import telepot
import pexpect
import os
import sys
import re

#start python interpreter session in expect
session = pexpect.spawn('python3')
session.expect('>>>')

def handle(msg):
    global session
    chat_id = msg['chat']['id']
    command = msg['text']

    print("got command: {}".format(command))

    if command[:4] == '/run':
        cmd = command[command.find(' ')+1:]
        cmd = re.sub(r'#n','\n',cmd)
        session.sendline(cmd)
        session.expect(r'>>>|\.\.\.', timeout=15)
        print(session.before)
        bot.sendMessage(chat_id, session.before)

    elif command[:6] == '/reset':
        session.kill(0)
        session = pexpect.spawn('python3')
        session.expect('>>>')
        bot.sendMessage(chat_id, 'session reset')

    elif command[:8] == '/restart': #restart docker container
        sys.exit(0)		    #assumes setting 'restart: always'

    elif command[:5] == '/help':
        help_string =''
        special_str='lol'
        bot.sendMessage(chat_id, help_string + special_str)



mykey = os.environ['TELEKEY'] #yaml.load(cfgstr)['key']
bot = telepot.Bot(mykey)

bot.message_loop(handle, run_forever=True)
print("i'm listening yo")
