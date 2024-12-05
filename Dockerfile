FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot

VOLUME ["/data"]

CMD ["python", "-m", "bot.bot"]