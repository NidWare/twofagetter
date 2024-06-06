FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py main.py
COPY config.yml config.yml

VOLUME ["/app/db"]

CMD ["python", "main.py"]
