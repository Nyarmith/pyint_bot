# @pyint_bot
## Username: PyInt_bot


Endpoints:  
* /run  cmd                 Runs a command in the same python interpreter
    * #n exapnds into a newline and #t expands into 4 spaces, for multiline statments
* /save [cmd]  saves given cmd or the last one run
* /list lists saved snippets
* /ctrlc keyboard ctrlc interrupt
* /reset resets the state

To use the bot in a new chat, you must run _/start_

TODO:
* Make stdout and stderr go to same stream, current threading model seems to totally ignore stderr due to threading
    * could be buffering? check buffering related settings in Popen PIPE and set to 0
* No logging occurs on exceptions in docker. Make docker log those maybe by changing a run setting.
* Add per-chat streams. Could be done with per-chat subprocess.
    * eventual goal, is to send new chat message on every new prompt (empty >>>)
