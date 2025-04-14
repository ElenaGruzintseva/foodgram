FROM python:3.9

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY backend/ .

COPY local/entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
