#!/usr/bin/python3
import telepot
import pexpect
import os
import sys
import re

#class for getting output from pexpect
class fauxlog:
    def __init__(self):
        self.str=b''

    def write(self, line):
        self.str += line
        print(self.str)

    def flush(self):
        #print('callign flush\n')
        pass

    def pop(self):
        copy = self.str
        self.str = b''
        #cleaning
        ind1= copy.find(b'\n')
        ind2 = copy.rfind(b'\n')
        copy = copy[ind1+1:ind2]
        copy = copy.split(b'\n')
        for line in copy:
            if line.find(b'...') == 0:
                copy.remove(line)
        for i in range(1,len(copy)):
            if copy[i-1] == copy[i]:
                del copy[i]

        return b'\n'.join(copy)

logger_obj = fauxlog()

#start python interpreter session in pexpect
session = pexpect.spawn('python3')
session.expect('>>>')
session.logfile = logger_obj

#almost the same as pexpect.spawn.writelines(), but with output
def writelines(cmds):
    global logger_obj
    global session

    for line in cmds:
        session.sendline(line)
        session.expect(r'>>>|\.\.\.', timeout=15)

    return logger_obj.pop()

#main handle loop
def handle(msg):
    global session
    chat_id = msg['chat']['id']
    command = msg['text']

    print("got command: {}".format(command))

    if command[:4] == '/run':
        cmd = command[command.find(' ')+1:]
        cmd = re.sub(r'#t','    ',cmd)
        res = writelines(cmd.split('#n'))
        print(res)
        bot.sendMessage(chat_id, res)

    elif command[:6] == '/reset':
        session.kill(0)
        session = pexpect.spawn('python3')
        session.expect('>>>')
        logger = fauxlog()
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
