FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create static and media directories
RUN mkdir -p staticfiles media

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
