#!/venv/bin/python3

import time, os
import pickle
import configparser
import telepot

class Movies(object):
    empty_chat = { 'list':[], 'finished':[] }

    def __init__(self):
        self.movies = {}

    def new_chat(self, chat_id):
        self.movies[chat_id] = self.empty_chat

    def add_movie(self, chat_id, movie):
        f = os.path.join('chats',str(chat_id))

        try:
            chatfile = open(f, 'rb')

            old_list = pickle.load( chatfile )
            if movie not in old_list['list']:
                old_list['list'].append(movie)
            else:
                # movie already added
                return -1

            chatfile.close()
            chatfile = open(f, 'wb')
            pickle.dump( old_list, chatfile )
            chatfile.close()

            return 0

        except (EOFError, IOError, FileNotFoundError) as e:
            # file is empty
            chatfile = open(f, 'wb')

            g = {}
            g['list'] = [movie]
            g['finished'] = []

            pickle.dump(g, chatfile)
            chatfile.close()

            return 0

    def list_movies(self, chat_id):
        try:
            f = os.path.join('chats',str(chat_id))
            chatfile = open(f, 'rb')

            old_list = pickle.load( chatfile )
            chatfile.close()

            ret = ''
            for i in range(0, len(old_list['list'])):
                ret += "{}: {}\n".format(i+1, old_list['list'][i])
            return ret
        except (IOError, EOFError) as e:
            # chat doesn't have a list (or file is empty)
            return -1

    def watched_a_movie(self, chat_id, movie):
        f = os.path.join('chats',str(chat_id))

        try:
            chatfile = open(f, 'rb')

            g = pickle.load( chatfile )
            old_list = g['list']
            finished = g['finished']
            if movie in old_list:
                old_list.remove(movie)
            if movie not in finished:
                finished.append(movie)

            chatfile.close()
            chatfile = open(f, 'wb')
            pickle.dump(g, chatfile)
            chatfile.close()

        except (EOFError, IOError, FileNotFoundError) as e:
            # file is empty (what?)
            chatfile = open(f, 'wb')

            g = {}
            g['list'] = []
            g['finished'] = [movie]

            pickle.dump(g, chatfile)
            chatfile.close()

            return 0
        
    def finished_movies(self, chat_id):
        try:
            f = os.path.join('chats',str(chat_id))
            chatfile = open(f, 'rb')

            old_list = pickle.load( chatfile )
            chatfile.close()

            ret = ''
            for i in range(0, len(old_list['finished'])):
                ret += "{}: {}\n".format(i+1, old_list['finished'][i])
            return ret
        except (IOError, EOFError) as e:
            # chat doesn't have a list (or file is empty)
            return -1



# help info
help_string = " Movie List Bot! A bot for keeping track of movies to watch with your friends. \n\
/add        Add a movie to your watchlist \n\
/list       List of movies to watch \n\
/watched    Tell movie_list_bot you've watched this movie (and remove it from your watchlist) \n\
/finished   List of movies your group has finished "

movies = Movies()

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print("got command: {}".format(command))

    # Add a movie to the watchlist (creates the group if it didn't exist yet)
    if command[:4] == '/add':
        first_space = command.index(' ')
        moviename = command[first_space+1:]
        if not moviename.strip():
            bot.sendMessage(chat_id, "Make sure to include a movie title with /add")
        else:
            ret = movies.add_movie(chat_id, moviename)

            if ret == 0:
                bot.sendMessage(chat_id, "{} added to list".format(moviename))
            else:
                bot.sendMessage(chat_id, "{} already on list".format(moviename))

    # Get the movie watchlist
    elif command[:5] == '/list':
        ret = movies.list_movies(chat_id)
        if ret == -1:
            bot.sendMessage(chat_id, "No movie list yet! Add movies with /add")
        else:
            bot.sendMessage(chat_id, "Your list:\n{}".format(ret))

    # Get the list of finished movies
    elif command[:9] == '/finished':
        ret = movies.finished_movies(chat_id)
        if ret == -1:
            bot.sendMessage(chat_id, "This chat finished any movies!")
        else:
            if not ret.strip():
                bot.sendMessage(chat_id, "You haven't watched any movies yet! Add them with /watched")
            else:
                bot.sendMessage(chat_id, "You've watched: \n{}".format(ret))

    # Mark a movie as watched
    elif command[:8] == '/watched':
        first_space = command.index(' ')
        moviename = command[first_space+1:]

        if not moviename.strip():
            bot.sendMessage(chat_id, "Make sure to include a movie title with /watched")
        else:
            movies.watched_a_movie(chat_id, moviename)
            bot.sendMessage(chat_id, "Added {} to your finished list!".format(moviename))

    elif command[:7] == '/modify':
        first_space = command.index(' ')
        movienum = command[first_space+1:]

        pass

    # help string
    elif command[:5] == '/help':
        bot.sendMessage(chat_id, help_string)


config = configparser.ConfigParser()
config.read('config.ini')
key = config['DEFAULT']['key']
bot = telepot.Bot(key)

bot.message_loop(handle)
print("i'm listening yo")

while 1:
    time.sleep(10)
