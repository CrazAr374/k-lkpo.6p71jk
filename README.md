# Adobe Hackathon 2025 – Intelligent PDF Analysis Suite

## Overview

This repository contains two modular yet interlinked tools developed for Adobe’s Hackathon Challenge:

| Challenge | Module         | Purpose                                                                                                                                                 |
| --------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1A**    | `Challenge_1a/` | Automatically extract structured **section outlines (headings and subheadings)** from multilingual PDF documents                                        |
| **1B**    | `Challenge_1b/` | Extract **relevant content sections** from PDFs using a **persona-driven ranking system**, optimized for literature reviews or goal-based summarization |

Together, these tools provide an advanced, fast, and offline-compatible pipeline for navigating and understanding large or complex PDF documents.

---

## Challenge 1A – Hybrid Outline Extractor

**Goal**: Automatically extract document structure by identifying heading hierarchies (H1, H2, H3) from PDFs.

### How It Works:

* Uses **visual layout features**: font size, bold text, underline, alignment
* Combines with **language-based signals**: multilingual heading keywords (English, Hindi, Japanese, etc.)
* Applies a **hybrid scoring mechanism** to classify lines as H1/H2/H3
* Groups headings into a **hierarchical outline**
* Infers the title of the document based on metadata or largest centered text

### Output:

* A structured `outline` per PDF in JSON format
* Each entry includes heading level, page number, and formatting info

> Works well with resumes, research papers, and multilingual PDFs.

---

## Challenge 1B – Persona-Driven Section Extractor

**Goal**: Extract and rank the **most relevant content sections** from multiple PDFs, based on a **user's persona and goal**.

### How It Works:

* Takes input from a `persona.json` file (e.g., a researcher's role and goal)
* Parses PDFs using `PyMuPDF` and identifies candidate sections based on content cues
* Uses **TF-IDF similarity** between document sections and the persona-goal query
* Boosts scores using **domain-specific keywords**
* Outputs structured JSON with:

  * Ranked relevant sections
  * Summary sentences
  * Keywords
  * Page references for navigation

> Designed for researchers, analysts, and professionals who want targeted content from large documents.

---

## Why Our Models Are Different and Better

| Feature                    | Traditional Extractors        | Our Model                                                 |
| -------------------------- | ----------------------------- | --------------------------------------------------------- |
| **Multilingual Support**   | Rarely supported              | Handles English, Hindi, French, Spanish, Japanese       |
| **Hybrid Feature Scoring** | Usually font-size only        | Combines font, boldness, alignment, caps, and keywords  |
| **Structured Output**      | Often flat or ungrouped       | Nested heading hierarchy with H1–H3 levels              |
| **Persona Awareness**      | Not supported                 | Personalized extraction based on user intent            |
| **Lightweight & Offline**  | Often model-heavy/cloud-based | Runs locally in Docker, fast and memory-efficient       |
| **Fallback Safety**        | Fails on noisy PDFs           | Uses smart defaults and fallback logic to ensure output |

---

## Folder Structure

```
root/
│
├── challenge1a/         # Heading extraction (outline structure)
│   ├── process.py
│   ├── Dockerfile
│   ├── input/
|   ├── requirements.txt     # Shared dependencies
│   └── output/
│
├── challenge1b/         # Persona-driven content summarization
│   ├── process.py
│   ├── Dockerfile
|   ├── requirements.txt     # Shared dependencies
│   ├── persona.json     # Define user role + goal
│   ├── input/
│   └── output/
│
└── README.md            # This file
```

---

## Getting Started

Each module has its own Dockerfile and can run independently:

### For Challenge 1A:

```bash
cd challenge1a
docker build -t pdf-outline-extractor .
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" pdf-outline-extractor
```

### For Challenge 1B:

```bash
cd challenge1b
docker build -t persona-extractor .
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" -v "$(pwd)/persona.json:/app/persona.json" persona-extractor
```

---

## Summary

This dual-model toolkit aims to **bridge the gap between document structure and meaning** by combining intelligent heading detection with personalized content extraction.

By prioritizing **lightweight processing**, **human-centered design**, and **real-world resilience**, our solution is built for practical and powerful PDF exploration—offline, multilingual, and fast.
