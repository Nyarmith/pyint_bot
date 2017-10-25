# Telegram bot key must be passed through the
# environment variable TELEKEY
FROM frolvlad/alpine-python3

VOLUME /opt/list_bot/chats

WORKDIR /opt/list_bot/

RUN pip install telepot && pip install pexpect

ADD pint_bot_docker.py .

CMD python3 pint_bot_docker.py
