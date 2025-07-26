# Challenge 1A – PDF Outline Extractor

## What the Model Does

This solution extracts a structured outline from any PDF file by detecting headings and subheadings and organizing them into a hierarchical format (H1, H2, H3). It is built using a **hybrid scoring model** that leverages both **layout-based cues** (such as font size, boldness, and position) and **textual signals** (such as multilingual keywords and common patterns).

The final output is a clean JSON file representing the detected document structure. It works effectively across a wide variety of documents including academic papers, resumes, scanned text documents, and multilingual content.

---

## Why It’s Better Than Baseline

| Feature                      | Our Solution                           | Baseline Approaches               |
| ---------------------------- | -------------------------------------- | --------------------------------- |
| **Heading Detection Method** | Hybrid (visual + keyword-based)        | Mostly visual or rule-based       |
| **Multilingual Capability**  | Yes (English, Hindi, Japanese, etc.)   | Often English-only                |
| **Fallback Logic**           | Yes, ensures partial output always     | May fail silently on noisy PDFs   |
| **Offline Support**          | Fully offline, no API required         | Some rely on external services    |
| **Containerization**         | Fully Dockerized and portable          | May require system-specific setup |
| **Hierarchy Construction**   | Yes, clean JSON tree with H1-H3 levels | Flat or loosely structured        |

---

## How It Works

1. **Text and Feature Extraction**
   Each page is processed using PyMuPDF to extract text, formatting styles (bold, underline), font sizes, and positional information.

2. **Hybrid Heading Scoring**
   A score is assigned to each line using a set of weighted heuristics:

   * Font size vs. body text size
   * Formatting: bold, underlined, all-caps
   * Centered alignment
   * Heading patterns (e.g., numbered titles)
   * Keyword match in multiple languages

3. **Heading Classification and Nesting**
   Headings are assigned to H1, H2, or H3 based on font size clusters. Then they are nested into a tree structure according to layout flow and page order.

4. **Title Inference**
   If metadata is available, it uses that; otherwise, it selects the topmost large-sized, bold-centered line on the first page.

5. **JSON Output**
   For each PDF, the output JSON includes:

   * `title`: inferred title of the document
   * `outline`: structured headings with formatting, page number, and hierarchy level

---

## Folder Structure

```
challenge1a/
├── Dockerfile            # Docker build configuration
├── requirements.txt      # Python dependencies
├── process.py            # Main script to extract headings
├── input/                # Add your PDF files here
│   └── sample.pdf
├── output/               # JSON output files will be saved here
│   └── sample.json
```

---

## Quick Usage Instructions

### Step 1: Build the Docker Image

```bash
docker build -t pdf-outline-extractor .
```

### Step 2: Add PDF Files

Place one or more PDF files into the `input/` folder.

### Step 3: Run the Extraction

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-outline-extractor
```

### Step 4: View Output

Output files will be saved as `.json` in the `output/` folder. Each contains the heading hierarchy.

---

## Example Output (JSON)

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

* **Hybrid Scoring**: Uses both layout and content patterns
* **Language-Aware**: Supports English, Hindi, Japanese, Spanish, and French
* **Resilient Output**: Generates meaningful JSON even with noisy or inconsistent documents
* **Lightweight**: Runs fully offline and has low memory usage
* **Dockerized**: Portable and consistent across platforms

---

## Requirements (For Local Use)

If not using Docker:

```bash
pip install -r requirements.txt
```

### Dependencies:

* `PyMuPDF (fitz)`
* `unicodedata`, `json`, `re`, `collections`

---

## Performance

* Processes 3–5 PDFs in under 5 seconds each
* Memory usage remains under 100 MB
* Output JSON is compact, typically under 200 KB per document

