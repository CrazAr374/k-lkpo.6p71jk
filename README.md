# Adobe Hackathon 2025 – Intelligent PDF Analysis

## Overview

This repository presents a dual-system solution developed for Adobe Hackathon 2025. The goal is to enable **intelligent understanding and navigation of complex PDF documents** using lightweight, offline-compatible tools.

The project is divided into two interconnected but standalone modules:

| Challenge | Folder         | Purpose                                                                |
| --------- | -------------- | ---------------------------------------------------------------------- |
| 1A        | `challenge1a/` | Extracts a structured outline (H1, H2, H3) from multilingual PDFs      |
| 1B        | `challenge1b/` | Extracts and ranks content sections based on a user's persona and goal |

Together, they provide an end-to-end document intelligence pipeline suitable for researchers, analysts, and developers working with large or unstructured PDF files.

---

## Challenge 1A – Hybrid Outline Extractor

**Objective:** Extract document structure by detecting and classifying headings (H1, H2, H3) from PDFs, even when multilingual or poorly formatted.

### How It Works

* **Visual Features:** Analyzes font size, boldness, underline, alignment, and capitalization.
* **Language Signals:** Detects heading-like phrases using multilingual keywords (supports English, Hindi, Japanese, Spanish, French).
* **Hybrid Scoring System:** Assigns heading levels based on both visual layout and linguistic patterns.
* **Hierarchy Construction:** Groups extracted headings into a nested structure, forming an outline.
* **Fallback Logic:** Ensures useful output even from noisy or unstructured PDFs.

### Output

Each input PDF produces a JSON file containing:

* Document title (inferred from metadata or visual cues)
* Structured heading outline with H1–H3 levels
* Formatting metadata (page, size, bold, alignment, etc.)

Useful for processing academic papers, resumes, reports, and scanned PDFs with embedded text.

---

## Challenge 1B – Persona-Based Section Extractor

**Objective:** Extract and summarize the most relevant sections from one or more PDFs based on a defined **persona** and their **task or objective**.

### How It Works

* Reads user input from a `persona.json` file describing role and intent.
* Parses PDFs to identify candidate sections.
* Computes **TF-IDF similarity** between sections and persona/task.
* Boosts ranking using pre-defined domain keywords (e.g., “methodology,” “benchmark,” “compliance”).
* Generates a structured JSON output with:

  * Ranked relevant sections
  * Key keywords
  * Concise summaries
  * Page references and source context

### Output

For each run, produces a single JSON result file with:

* Input metadata (files, persona, timestamp)
* Scored and ranked sections
* Summary sentences from each section
* Keywords and page-level metadata
* Subsections with refined extracted highlights

Ideal for literature reviews, grant preparation, policy analysis, or industry research.

---

## Why Our Models Stand Out

| Feature                  | Common Solutions                       | Our Models                                              |
| ------------------------ | -------------------------------------- | ------------------------------------------------------- |
| Multilingual PDF Support | Rare or incomplete                     | Full support for English, Hindi, French, Japanese, etc. |
| Hybrid Scoring           | Usually layout-based only              | Combines layout, text patterns, and semantic cues       |
| Heading Hierarchy        | Often flat or shallow                  | Nested H1–H3 output with contextual relevance           |
| Persona Adaptability     | Not supported                          | Customizable persona-specific section ranking           |
| Lightweight & Offline    | Many depend on external APIs or models | Fully offline after Docker build, <100MB memory use     |
| Resilience on Poor PDFs  | Prone to failure                       | Uses fallback logic to ensure partial useful output     |

---

## Folder Structure

```
root/
├── challenge1a/               # Heading extraction (outline generator)
│   ├── process.py
│   ├── Dockerfile
│   ├── input/
│   ├── output/
│   └── requirements.txt
│
├── challenge1b/               # Persona-based section extractor
│   ├── process.py
│   ├── Dockerfile
│   ├── input/
│   ├── output/
│   ├── persona.json
│   └── requirements.txt
│
└── README.md                  # This file
```

---

## 🚀 Getting Started

Each module is containerized via Docker and can be run independently.

### Run Challenge 1A: Outline Extractor

```bash
cd challenge1a
docker build -t pdf-outline-extractor .
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-outline-extractor
```

### Run Challenge 1B: Persona-Based Extractor

```bash
cd challenge1b
docker build -t persona-extractor .
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/persona.json:/app/persona.json" \
  persona-extractor
```

On Windows (PowerShell), replace `$(pwd)` with `$(Get-Location)`.

---

## Summary

This repository demonstrates a two-part solution that bridges the gap between **document structure (Challenge 1A)** and **semantic meaning (Challenge 1B)**.

It is designed to operate **efficiently and reliably across real-world documents**, including multilingual and semi-structured PDFs. By focusing on hybrid scoring, offline usability, and modular design, this tool offers a robust framework for intelligent document processing—adaptable for industry, academia, and enterprise applications.
