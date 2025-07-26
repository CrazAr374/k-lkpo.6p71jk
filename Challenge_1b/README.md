# Challenge 1B – Persona-Based PDF Section Extractor

This tool is designed for Adobe Hackathon – Challenge 1B. It helps identify the most relevant sections from a set of PDF documents, based on the user's role and the task they need to accomplish. It combines lightweight Natural Language Processing (NLP), TF-IDF-based section scoring, and smart keyword summarization to deliver focused and useful insights.

---

## What This Project Does

* Understands your **persona** and **objective**
* Scans multiple PDFs and extracts relevant sections
* Uses keyword-driven logic and ranking algorithms
* Summarizes top content with brief insights
* Produces a clean and structured JSON output

---

## Folder Structure

```
challenge1b/
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── process.py              # Main script
├── persona.json            # Input: user's persona and task
├── input/                  # Folder for your PDFs
└── output/                 # JSON output will be saved here
```

---

## How to Use This Tool

### Step 1: Build the Docker Image

Open your terminal and run:

```bash
docker build -t persona-extractor .
```

### Step 2: Add Your Inputs

1. Place your PDF files inside the `input` folder.
2. Create or edit the `persona.json` file like this:

```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Create a literature summary focused on methods, datasets, and benchmarks"
}
```

### Step 3: Run the Tool

#### On Linux or macOS:

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/persona.json:/app/persona.json" \
  persona-extractor
```

#### On Windows (Command Prompt):

```cmd
docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" -v "%cd%\persona.json:/app/persona.json" persona-extractor
```

#### On Windows (PowerShell):

```powershell
docker run --rm `
  -v "$(Get-Location)\input:/app/input" `
  -v "$(Get-Location)\output:/app/output" `
  -v "$(Get-Location)\persona.json:/app/persona.json" `
  persona-extractor
```

---

## Output

After processing, you will find the results in:

```
output/result.json
```

The JSON contains:

* Input metadata
* Ranked and scored relevant sections
* Extracted keywords and summaries
* A breakdown of subsections with contextual highlights

---

## Example Output Structure

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Create a literature summary...",
    "processing_timestamp": "2025-07-26T12:00:00"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page": 3,
      "section_title": "Proposed Methodology",
      "importance_rank": 0.843,
      "keywords": ["dataset", "algorithm", "benchmark"],
      "summary": "This method improves accuracy using XYZ...",
      "sub_sections": [
        {
          "refined_text": "Our approach boosts accuracy by 12% on ABC dataset.",
          "document": "doc1.pdf",
          "page": 3
        }
      ]
    }
  ]
}
```

---

## How the System Works

1. **Persona Input**
   The script reads your persona and goal from `persona.json`.

2. **PDF Parsing**
   Each page of every PDF is scanned using PyMuPDF to extract text.

3. **Section Scoring**
   Sections are ranked using TF-IDF similarity and domain-specific keyword boosts.

4. **Keyword Extraction and Summarization**
   Important words and high-value sentences are selected using frequency and length rules.

5. **Output Compilation**
   Results are formatted into a structured JSON for easy reading or further processing.

---

## Key Features

* Lightweight and fast (2–5 seconds for 3–5 PDFs)
* Fully offline after Docker build
* Prioritizes keywords relevant to scientific, technical, and financial domains
* Works across different personas and research domains
* Summarizes each section into clear, short points
* Modular and easy to customize

---

## Technology Stack

* Python 3.9 (via Docker)
* PyMuPDF (`fitz`) for PDF text extraction
* scikit-learn for TF-IDF vectorization and cosine similarity
* NLTK for sentence tokenization
* NumPy and standard libraries for processing and logic

---

## Customization Guide

### Update Persona and Goals

Change the `persona.json` file to fit your use case.

### Prioritize Different Keywords

Modify the `BOOST_KEYWORDS` list in `process.py` to focus on your domain-specific vocabulary.

### Adjust Output Summary

You can modify `extract_summary()` if you want to increase or decrease the number of sentences.

---

## Performance

* Processes files within seconds
* Uses less than 100 MB of memory
* Requires no internet after Docker image build
* Works well even with longer technical PDFs
