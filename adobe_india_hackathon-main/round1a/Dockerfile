# Multi-stage build for optimal size
FROM python:3.9-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY *.py ./

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH
ENV TESSERACT_CMD=tesseract
ENV INPUT_DIR=/app/input
ENV OUTPUT_DIR=/app/output

# Set proper permissions
RUN chmod +x /app/main.py

# Run the application
CMD ["python", "main.py"]
