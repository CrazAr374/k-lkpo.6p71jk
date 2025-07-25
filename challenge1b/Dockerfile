# Use a lightweight Python base image
FROM python:3.9-slim

WORKDIR /app

COPY process.py .
COPY persona.json .
COPY requirements.txt .

RUN pip install torch==2.0.1+cpu torchvision --extra-index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt \
 && python -c "import nltk; nltk.download('punkt')" \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L6-v2')"

# Create input and output folders
RUN mkdir -p input output

CMD ["python", "process.py"]
