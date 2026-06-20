FROM python:3.11-slim

# Install ffmpeg and required system packages
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade yt-dlp

# Copy all project files
COPY . .

# Ensure the output and videos folders exist
RUN mkdir -p output videos

# Run the telegram bot
CMD ["python", "telegram_bot.py"]
