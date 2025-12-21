
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/
# Don't copy .env in image, assume mounted or injected

# Create logs directory
RUN mkdir -p logs data

EXPOSE 8000

ENV PYTHONPATH=/app
ENV PORT=8000

CMD ["python", "src/main_minimal.py"]
