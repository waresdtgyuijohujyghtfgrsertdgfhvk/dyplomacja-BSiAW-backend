FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*


RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]
