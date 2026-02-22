# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all your project files into the container
COPY . .

# BRUTE FORCE INSTALL: Ignore requirements.txt and force install everything directly
RUN pip install --no-cache-dir fastapi uvicorn httpx supabase python-dotenv

# Start the server using Railway's dynamic PORT variable
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]