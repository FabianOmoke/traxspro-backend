# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy just the requirements file first to cache the installations
COPY requirements.txt .

# Install dependencies globally inside the container (no venv needed!)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files into the container
COPY . .

# Start the server using Railway's dynamic PORT variable
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT