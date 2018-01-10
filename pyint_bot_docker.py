#!/usr/bin/python3
import telepot
import telepot.text as telefmt
import queue
import yaml
import os
import subprocess
import threading
import time
import sys
import re
import pdb
import signal



savefile='chats/snippets'

#storage for empty /save cmd
lastcmd=''
lastusr=''

listedlast = 0

#stdout and stderr queues
outq = queue.Queue()

if os.path.isfile(savefile):
    global snippets
    f = open(savefile)
    snippets=yaml.load(f.read())
    f.close()
else:
    snippets={} #format { chat_id_1:[ [snippet, user_id], [], [] ... ], chat_id_2:[ ... ] }

def save():
    f = open(savefile,'w')
    f.write(yaml.dump(snippets))
    f.close()

#threaded output readers
def stdout_reader(proc, q):
    for line in iter(proc.stdout.readline,b''):
        q.put(line.decode('utf-8'))

def stderr_reader(proc, q):
    for line in iter(proc.stderr.readline,b''):
        l = line.decode('utf-8')
        l=re.sub(r'>>> |\.\.\. ','',l)
        q.put(l)

def dumpq(Q):
    ret=''
    for i in range(0,Q.qsize()):
        ret += Q.get()
    return ret

proc = subprocess.Popen(['python3','-i'],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)

#args seem necessary to bind outside vars to a thread(i.e. no globals)
out_t = threading.Thread(target=stdout_reader,args=(proc,outq))
err_t = threading.Thread(target=stderr_reader,args=(proc,outq))
#these aren't running concurrently due to the GIL goddamnit
out_t.start()
err_t.start()


#main handle loop
def handle(msg):
    global listedlast
    global lastcmd
    global lastusr
    global proc
    global out_t
    global err_t
    chat_id = msg['chat']['id']
    command = msg['text']
    fromusr = msg['from'] #{'first_name':<users first name>, 'id': <users id>}

    print('got command: {}'.format(command))

    if command[:4] == '/run':
        cmd = command[command.find(' ')+1:]
        cmd = re.sub(r'#t','    ',cmd)
        cmd = (cmd.split('#n'))
        cmd = '\n'.join(cmd) + '\n'
        print('formatted cmd:{}'.format(cmd))

        #pdb.set_trace()
        proc.stdin.write(cmd.encode())
        proc.stdin.flush()

        time.sleep(.25)

        rsp = dumpq(outq)
        if (rsp != ''):
            #rsp = '```python\n'+cmd + '--------\n' + rsp + '\n```'
            rsp = cmd + '--------\n' + rsp 
            bot.sendMessage(chat_id, rsp)

        lastcmd=cmd
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
        start=listedlast+1
        #formatting may cause issues, look at https://stackoverflow.com/questions/21864192/most-elegant-way-to-format-multi-line-strings-in-python if necessary
        while listedlast <  m and listedlast < len(snippets[chat_id]):
            rsp += '\n#{} <pre>\n{}\n</pre>' \
                   ' \--submitted by <a href=\"tg://usr?id={})\">@{}</a>\n' \
                   .format(listedlast+1,
                           snippets[chat_id][listedlast][0],
                           snippets[chat_id][listedlast][1]['id'],
                           snippets[chat_id][listedlast][1]['first_name'])
            listedlast += 1

        rsp += '\n [{},{}] of {}'.format(start,listedlast,len(snippets[chat_id]))

        if listedlast == len(snippets[chat_id]):
            listedlast = 0

        #rsp = telefmt.apply_entities_as_html(rsp,[])
        bot.sendMessage(chat_id, rsp,parse_mode='html')

    elif command[:7] == '/remove':
        #accept id(i.e. number of input in its order)
        #and remove that from the list
        n = command.split()
        try:
            num=int(n[1])-1
            if len(snippets[chat_id]) >= num or num < 0:
                bot.sendMessage(chat_id,
                    'error, {} out of range: [1,{}]'.format(n,len(snippets[chat_id])))
            else:
                del snippets[chat_id][num]

        except:
            bot.sendMessage(chat_id, 'error, {} not a number'.format(n[1]))

    elif command[:6] == '/reset':
        proc.terminate()
        out_t.join()
        err_t.join()
        proc = subprocess.Popen(['python3','-i'],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE)

        out_t = threading.Thread(target=stdout_reader,args=(proc,outq))
        err_t = threading.Thread(target=stderr_reader,args=(proc,outq))
        out_t.start()
        err_t.start()

    elif command[:8] == '/restart': #restart docker container
        sys.exit(0)		    #assumes setting 'restart: always'

    elif command[:6] == '/start':
        try:
            snippets[chat_id]
        except:
            snippets[chat_id] = []
        save()

    elif command[:6] == '/ctrlc':
        proc.send_signal(signal.SIGINT)
        time.sleep(.25)
        rsp = dumpq(outq)
        if rsp != '':
            bot.sendMessage(chat_id, rsp)
        else:
            bot.sendMessage(chat_id, 'KeyboardInterrupt')

    elif command[:5] == '/help':
        help_string =''
        special_str='lol'
        bot.sendMessage(chat_id, help_string + special_str)

    if listedlast != 0 and command[:5] != '/list':
        listedlast = 0



mykey = os.environ['TELEKEY'] #yaml.load(cfgstr)['key']
bot = telepot.Bot(mykey)

bot.message_loop(handle, run_forever=True)
print("i'm listening yo")
