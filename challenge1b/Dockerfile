# Use a lightweight Python base image
FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

COPY process_persona.py .
COPY persona.json .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create input and output folders
RUN mkdir -p input output

CMD ["python", "process_persona.py"]
