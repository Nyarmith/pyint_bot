# Telegram bot key must be passed through the
# environment variable TELEKEY
FROM frolvlad/alpine-python3

#RUN useradd -m -u 1020 telebot

#USER telebot

#WORKDIR /home/telebot/

ADD list_bot_docker.py .

CMD python3 list_bot_docker.py
