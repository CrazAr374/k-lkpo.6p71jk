# Challenge 1A – PDF Outline Extractor

## Overview

This project is designed to intelligently extract a structured outline (headings and subheadings) from PDF documents. It uses a hybrid scoring method that combines visual features (like font size and boldness) with textual cues (like multilingual heading keywords) to identify sections accurately, even in complex or multilingual PDFs.

The tool is built to be lightweight, fast, and effective even when processing diverse types of documents like academic papers, resumes, or scanned materials with embedded text.
---
## How It Works

The solution works by processing each page of a PDF and identifying potential headings using a mix of layout-based and keyword-based logic. Here's a simplified breakdown:

1. **Text Extraction**:
   The tool uses `PyMuPDF` to extract text, font sizes, formatting flags (like bold and underlined), and position information from every line of every page.

2. **Hybrid Heading Scoring**:
   For each line of text, it calculates a "heading score" based on:

   * Font size relative to the body text
   * Bold, centered, underlined, or colored text
   * Capitalization (all-caps headings)
   * Pattern-based cues (like numbered headings)
   * Presence of heading keywords (supports English, Hindi, French, Spanish, Japanese, etc.)

3. **Heading Hierarchy Construction**:

   * Scores are used to classify lines as H1, H2, or H3.
   * Headings are grouped into a nested hierarchy based on size and page layout.
   * Fallback logic ensures some output even when documents lack strong structure.

4. **Output**:

   * Each PDF produces a JSON file with extracted heading hierarchy (`H1`, `H2`, and `H3`).
   * Title is inferred from metadata, font size, or top of the first page.

---

## Folder Structure

```
challenge1a/
│
├── Dockerfile              # Docker setup for building and running the tool
├── requirements.txt        # Python package dependencies
├── process.py              # Main logic for heading extraction
├── input/                  # Folder to store PDF files to be processed
│   └── your_file.pdf
├── output/                 # Extracted heading outline in JSON format
│   └── your_file.json
```

---

## Quick Start

### Step 1: Build the Docker Image

```bash
docker build -t pdf-outline-extractor .
```

### Step 2: Prepare Input Files

* Place one or more PDF files into the `input/` folder.

### Step 3: Run the Extractor

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-outline-extractor
```

### Step 4: View Output

* Navigate to the `output/` folder to see the JSON files, one per input PDF.
* Each JSON contains structured headings and their assigned levels (H1, H2, H3), including page numbers and formatting info.

---

## Example Output

```json
{
  "title": "Deep Learning Advances",
  "outline": [
    {
      "text": "1. Introduction",
      "page": 1,
      "level": "H1",
      "bold": true,
      "centered": true,
      "size": 20,
      "children": [
        {
          "text": "Background",
          "page": 2,
          "level": "H2",
          "bold": false,
          "centered": false,
          "size": 16
        }
      ]
    }
  ]
}
```

---

## Key Features

* **Hybrid Heading Scoring**: Blends layout and language signals for better accuracy.
* **Multilingual Support**: Recognizes headings in English, Hindi, Spanish, French, Japanese.
* **Offline, Lightweight Design**: No internet required after Docker build. Very low memory footprint.
* **Fallback Resilience**: Produces partial output even in poorly structured or noisy PDFs.
* **Fully Containerized**: Easy to run on any platform with Docker.

---

## Requirements

Install Python packages using:

```bash
pip install -r requirements.txt
```

**Key Libraries:**

* `PyMuPDF` (fitz) for PDF parsing
* `unicodedata`, `re`, `json` for string handling
* `collections` for efficient data grouping

---

## Performance

* Processes \~3–5 PDFs in under 5 seconds each
* Memory usage under 100 MB
* JSON output size: minimal and structured
