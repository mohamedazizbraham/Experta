# Use Python 3.10+ for compatibility with the collections.abc patch
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY database.py .
COPY logic.py .

# Run the application
CMD ["python", "app.py"]
