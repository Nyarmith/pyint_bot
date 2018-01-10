#!/usr/bin/python3
import telepot
import queue
import yaml
import os
import subprocess
import threading
import sys
import re



savefile='chats/snippets'

#storage for empty /save cmd
lastcmd=''
lastusr=''

listedlast = 0

#stdout and stderr queues
outq=queue.Queue()
errq=queue.Queue()

snippets={} #format { chat_id_1:[ [snippet, user_id], [], [] ... ], chat_id_2:[ ... ] }
if os.path.isfile(savefile):
    f = open(savefile)
    snippets=yaml.load(f.read())
    f.close()

def save():
    f = open(savefile,'w')
    f.write(yaml.dump(snippets))
    f.close()

#threaded output readers
def stdout_reader(proc):
    for line in iter(proc.stdout.stderr,b''):
        outq.put(line.decode('utf-8'))

def stderr_reader(proc):
    for line in iter(proc.stderr.readline,b''):
        errq.put(line.decode('utf-8'))

def dumpq(Q):
    ret=''
    for i in range(0,Q.qsize()):
        ret += Q.get()
    return ret

proc = subprocess.Popen(['python3','-i'],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)

out_t = threading.Thread(target=stdout_reader,args=(proc))
err_t = threading.Thread(target=stdout_reader,args=(proc))

#main handle loop
def handle(msg):
    global session
    chat_id = msg['chat']['id']
    command = msg['text']
    fromusr = msg['from'] #{'first name':<users first name>, 'id': <users id>}

    print('got command: {}'.format(command))

    if command[:4] == '/run':
        cmd = command[command.find(' ')+1:]
        cmd = re.sub(r'#t','    ',cmd)
        res = (cmd.split('#n'))
        print(res)

        proc.stdin.write(res.encode())
        proc.stdin.flush()

        time.usleep(.25)

        rsp = dumpq(errq) + dumpq(outq)
        bot.sendMessage(chat_id, rsp)

        lastcmd=res
        lastusr=fromusr
 
    elif command[:5] == '/save':
        #save current snippet, or previous input as a snippet(with the previous submitter's author)
        if len(command.split()) == 1:
            #use last input
            if lastcmd != '':
                snippets[chat_id].append([lastcmd, lastusr])
        else:
            cmd = command[command.find(' ')+1:]
            cmd = re.sub(r'#t','    ',cmd)
            cmd = (cmd.split('#n'))
            snippets[chat_id].append([cmd, fromusr])

        save()

    elif command[:5] == '/list':
        #list saved snippets, 10 at a time
        m = listedlast + 10
        rsp=''
        #formatting may cause issues, look at https://stackoverflow.com/questions/21864192/most-elegant-way-to-format-multi-line-strings-in-python if necessary
        while listedlast <  m and listedlast < len(snippets[chat_id]):
            rsp += '\n#{}\n <pre>\n{}\n</pre>\n' \
                   ' \--submitted by <a href=\"tg://usr?id={}\">user_name_maybe?</a>\n' \
                   .format(listedlast, snippets[chat][listedlast][0], snippet[chat][listedlast][1])
            listedlast += 1

        rsp += '\n out of {}'.format(len(snippets[chat_id]))

        if listedlast == len(snippets[chat_id]):
            listedlast = 0

        bot.sendMessage(chat_id, rsp)

    elif command[:7] == '/remove':
        #accept id(i.e. number of input in its order)
        #and remove that from the list
        n = command.split()
        try:
            num=int(n)
            if len(snippets[chat_id]) >= num or num < 0:
                bot.sendMessage(chat_id, 'error, {} out of range'.format(n))
            else:
                del snippets[chat_id][num]

        except:
            bot.sendMessage(chat_id, 'error, {} not a number'.format(n))

    elif command[:6] == '/reset':
        proc.terminate()
        out_t.join()
        err_t.join()
        proc = subprocess.Popen(['python3','-i'],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE)

        out_t = threading.Thread(target=stdout_reader,args=(proc))
        err_t = threading.Thread(target=stdout_reader,args=(proc))

    elif command[:8] == '/restart': #restart docker container
        sys.exit(0)		    #assumes setting 'restart: always'

    elif command[:6] == '/start':
        snippets[chat_id] = []
        save()

    elif command[:5] == '/help':
        help_string =''
        special_str='lol'
        bot.sendMessage(chat_id, help_string + special_str)

    if listedlast and command[:5] != '/list':
        listedlast = 0


mykey = os.environ['TELEKEY'] #yaml.load(cfgstr)['key']
bot = telepot.Bot(mykey)

bot.message_loop(handle, run_forever=True)
print("i'm listening yo")
