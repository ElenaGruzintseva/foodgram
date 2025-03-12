FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir --timeout=1000

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
