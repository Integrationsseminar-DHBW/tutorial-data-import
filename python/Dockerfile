FROM python:3.12-slim

# Set environment variable to disable output buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["python", "src/upload_to_qdrant.py"]