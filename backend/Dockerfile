FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir --timeout=1000

CMD ["gunicorn", "--bind", "0.0.0.0:7000", "foodgram.wsgi"]
