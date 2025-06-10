FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy Django project
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Tailwind CLI globally (optional)
RUN npm install -g tailwindcss

EXPOSE 8000