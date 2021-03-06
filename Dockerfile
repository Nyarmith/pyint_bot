# Telegram bot key must be passed through the
# environment variable TELEKEY
#FROM python:3.7.0a2
FROM frolvlad/alpine-python3

VOLUME /opt/pyint_bot/chats

WORKDIR /opt/pyint_bot/

RUN pip install telepot && pip install pexpect && pip install pyyaml

ADD pyint_bot_docker.py .

CMD python3 pyint_bot_docker.py
