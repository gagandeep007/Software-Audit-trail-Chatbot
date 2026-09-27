FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (build-essential for chromadb compiling sometimes needed, but slim might have enough for pre-compiled wheels. Adding basic build tools just in case, though mostly wheels are used now).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the Gradio port
EXPOSE 7860

# Ensure environment variables are loaded
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "app.py"]
