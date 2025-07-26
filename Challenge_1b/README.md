# Challenge 1B – Persona-Based PDF Section Extractor

## What the Model Does

This tool is designed to extract the most relevant content from PDFs based on a user’s role ("persona") and their task or goal ("job to be done"). It intelligently parses multiple documents and identifies the top sections and subsections by relevance using a combination of lightweight NLP, TF-IDF-based scoring, and domain-aware keyword summarization. The output is a clean, structured JSON that offers immediate insights customized to the user’s objective.

---

## Why It’s Better Than a Baseline Model

| Feature                    | This Model                                       | Common Baselines                             |
| -------------------------- | ------------------------------------------------ | -------------------------------------------- |
| **Persona Awareness**      | Reads and adapts to persona-specific goals       | Typically generic, not role-specific         |
| **Ranking Mechanism**      | TF-IDF + keyword boost scoring                   | Often rule-based or full-text search only    |
| **Summarization**          | Sentence-level abstraction with contextual focus | Not always summarized; returns raw text      |
| **Multidocument Support**  | Handles multiple PDFs with merged output         | Often one file at a time                     |
| **Fully Offline & Fast**   | No internet needed; <5s for 3–5 PDFs             | Some depend on external APIs or slow parsing |
| **Customization Friendly** | Easily modify keyword focus, summary length      | Usually static and fixed logic               |

---

## How It Works

### 1. Persona Input

The model reads a JSON file that contains two fields:

* `persona`: Defines the user type (e.g., "Researcher", "Data Scientist")
* `job_to_be_done`: Describes the user’s task (e.g., "Summarize methods and benchmarks")

### 2. PDF Parsing

Each PDF is scanned using **PyMuPDF** to extract page-wise text content.

### 3. Section Scoring

Text blocks and headings are scored using **TF-IDF vectorization** relative to the persona and task, with a boost for predefined domain-specific keywords.

### 4. Keyword Extraction & Summarization

High-importance keywords are selected. Relevant sentences are extracted using basic sentence tokenization and ranked by content value.

### 5. Output Compilation

All information is structured into a JSON output, including:

* Ranked relevant sections
* Summaries of each section
* Key extracted terms
* Source document and page references

---

## Folder Structure

```
challenge1b/
├── Dockerfile            # Docker setup file
├── requirements.txt      # Python dependency list
├── process.py            # Core processing and logic
├── persona.json          # Input persona and task definition
├── input/                # Folder for PDF input files
├── output/               # Folder where result.json will be saved
```

---

## How to Use This Tool

### Step 1: Build Docker Image

```bash
docker build -t persona-extractor .
```

### Step 2: Add Input Files

Place all PDF files into the `input/` folder.

Create a `persona.json` file like:

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

#### On Windows (CMD):

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

## Output Format

The final structured output is saved in `output/result.json` and includes:

* Metadata about documents and persona
* Ranked sections with title, page number, and relevance score
* Extracted keywords and short summaries
* Subsections that highlight key evidence

### Example:

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

## Key Features

* **Persona-aware scoring**: Matches content to user goals
* **Efficient and offline**: Lightweight and Dockerized
* **Domain-adaptable**: Works well for research, business, and technical use cases
* **Readable summaries**: Provides digestible insights
* **Fully customizable**: Change keywords, personas, summary length with ease

---

## Performance Benchmarks

* Average time: \~2–5 seconds for 3–5 PDFs
* Memory footprint: < 100 MB
* No internet needed after Docker setup
* Scales efficiently for long academic PDFs
