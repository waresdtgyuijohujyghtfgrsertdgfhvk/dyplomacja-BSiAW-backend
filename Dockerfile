FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]
