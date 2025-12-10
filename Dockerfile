FROM node:20 AS frontbuild
WORKDIR /app
COPY vite ./vite
WORKDIR /app/vite
RUN npm install && npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=frontbuild /app/vite/dist ./vite/dist

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]
