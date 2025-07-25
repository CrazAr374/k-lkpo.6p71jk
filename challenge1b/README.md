# Persona-Driven PDF Section Extractor

## Overview

This tool reads multiple PDFs, understands a user's persona and goal, and extracts the most relevant sections using semantic similarity (MiniLM). Output is a structured JSON file.

## Folder Structure

```
.
├── process.py
├── requirements.txt
├── Dockerfile
├── persona.json
├── input/
│   └── *.pdf
├── output/
│   └── result.json
```

## How to Run

1. **Build the Docker image:**
   ```sh
   docker build -t persona-extractor .
   ```

2. **Place your PDFs in the `input/` folder.**

3. **Edit `persona.json` as needed.**

4. **Run the container:**
   ```sh
   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/persona.json:/app/persona.json persona-extractor
   ```

5. **Check `output/result.json` for results.**

## Tech Stack

- PyMuPDF (fitz) for PDF parsing
- nltk for text cleaning/splitting
- sentence-transformers (MiniLM) for semantic similarity
- scikit-learn for cosine similarity
- Docker for offline, CPU-only execution

## Output Format

- Metadata: input PDFs, persona, job, timestamp
- Extracted sections: document, page, section title, importance rank, sub-sections (refined text)

## Notes

- Entirely offline, CPU-only, <100MB model
- Processes 3–5 PDFs in 30–45 seconds
- Generalizes to any persona/domain

### Your goals:
- **Semantic search**: Use local MiniLM (or similar) embeddings for section ranking (must be <200MB, ideally ~67MB like Ollama’s models).
- **Keyword extraction**: Use KeyBERT (with the same embedding model).
- **Extractive summarization**: Use TextRank (from `sumy` or `gensim`) or similar, fully offline.
- **All models must be small and run offline.**

---

## 1. **Embedding Model Choice**

- **MiniLM-L6-v2** (from `sentence-transformers`) is ~80MB and is the smallest widely-used semantic embedding model for English. It is smaller than 200MB and works with both KeyBERT and semantic search.
- **Ollama’s models**: If you mean the “tinyllama” or similar, those are for text generation, not embeddings. For semantic search and KeyBERT, you need a sentence embedding model.
- **bge-small-en-v1.5**: ~120MB, also suitable for semantic search and KeyBERT.

**Conclusion:**  
- **MiniLM-L6-v2** is the best fit for your requirements (67–80MB, works with KeyBERT, semantic search, and is widely supported).

---

## 2. **Pipeline Overview**

- **PDF Parsing**: PyMuPDF
- **Persona Input**: JSON
- **Embedding Model**: MiniLM-L6-v2 (sentence-transformers)
- **Keyword Extraction**: KeyBERT (with MiniLM)
- **Summarization**: TextRank (from `sumy`)
- **Ranking**: Cosine similarity
- **Output**: JSON

---

## 3. **Requirements Update**

Add to `requirements.txt`:
```
PyMuPDF==1.24.1
nltk==3.8.1
sentence-transformers==2.2.2
keybert==0.7.0
sumy==0.10.0
scikit-learn==1.3.2
numpy==1.26.4
```

---

## 4. **Script Update Plan**

- Use MiniLM-L6-v2 for all embeddings.
- Use KeyBERT for keywords.
- Use TextRank for summaries.
- All processing is offline and model is <200MB.

---

## 5. **Dockerfile Update**

- Download MiniLM-L6-v2 at build time (as before).
- Install all dependencies.

---

## 6. **Ready to Implement**

**I will:**
- Update your `requirements.txt`
- Update your `process.py` to use MiniLM for embeddings, KeyBERT for keywords, and TextRank for summaries.
- Update your Dockerfile to pre-download the model.

**Proceeding with these changes
