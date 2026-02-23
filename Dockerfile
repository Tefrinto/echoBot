FROM python:3.14 AS echobot

RUN apt update && apt install -y ffmpeg libopus-dev

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
