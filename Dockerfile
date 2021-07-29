FROM python:3.7.11

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY src src

CMD python ./src/bot.py