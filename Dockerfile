FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py bot.py

VOLUME ["/app/db"]

CMD ["python", "bot.py"]
