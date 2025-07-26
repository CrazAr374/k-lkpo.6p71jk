# Persona-Driven PDF Section Extractor

## Overview

This tool reads multiple PDFs, understands a user's persona and goal, and extracts the most relevant sections using TF-IDF similarity. Output is a structured JSON file.

## Folder Structure

```
challenge1b/
│
├── Dockerfile
├── requirements.txt
├── process.py
├── persona.json         ✅ Persona input
├── input/               ✅ Folder containing input PDFs
│   └── your_file1.pdf
│   └── your_file2.pdf
├── output/              ✅ Output will be written here
```

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t persona-extractor .
```

### 2. Prepare Your Files

- **Place PDFs in `input/` folder**
- **Edit `persona.json` as needed** (see format below)

### 3. Run the Container

**PowerShell:**
```powershell
docker run --rm `
  -v "$(Get-Location)\input:/app/input" `
  -v "$(Get-Location)\output:/app/output" `
  -v "$(Get-Location)\persona.json:/app/persona.json" `
  persona-extractor
```

**CMD:**
```cmd
docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" -v "%cd%\persona.json:/app/persona.json" persona-extractor
```

**Bash/Linux:**
```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/persona.json:/app/persona.json" \
  persona-extractor
```

### 4. Check Results

Results will be in `output/result.json`

## Input Format

### persona.json
```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Create a literature summary focused on methods, datasets, and benchmarks"
}
```

## Expected Output

```json
{
  "metadata": {
    "input_documents": [
      "your_file1.pdf",
      "your_file2.pdf"
    ],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Create a literature summary focused on methods, datasets, and benchmarks",
    "processing_timestamp": "2025-07-25T16:36:01.573045"
  },
  "extracted_sections": [
    {
      "document": "your_file1.pdf",
      "page": 3,
      "section_title": "Proposed Methodology / Prototype",
      "importance_rank": 0.825,
      "keywords": ["dataset", "algorithm", "benchmark"],
      "summary": "This section introduces a new approach using XYZ algorithm for ABC problem...",
      "sub_sections": [
        {
          "refined_text": "This method shows performance improvement of 10% on XYZ dataset.",
          "document": "your_file1.pdf",
          "page": 3
        }
      ]
    }
  ],
  "subsection_analysis": [
    {
      "document": "your_file1.pdf",
      "refined_text": "This method shows performance improvement of 10% on XYZ dataset.",
      "page": 3
    }
  ]
}
```

## Tech Stack

- **PyMuPDF (fitz)** for PDF parsing
- **nltk** for text cleaning/splitting
- **scikit-learn** for TF-IDF similarity
- **numpy** for numerical operations
- **Docker** for offline, CPU-only execution

## Performance

- **Processing Time**: 2-5 seconds for 3-5 PDFs
- **Memory Usage**: <100MB
- **Fully Offline**: No internet required after build
- **Lightweight**: No heavy ML models

## Troubleshooting

### Common Issues

1. **No sections found**
   - Ensure PDFs contain text (not just images)
   - Check that PDFs are not corrupted

2. **Permission errors**
   - Ensure input/output folders exist and are writable

### Debug Mode

Run interactively to see detailed logs:
```bash
docker run -it --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/persona.json:/app/persona.json" \
  persona-extractor
```

## Features

✅ **TF-IDF Search**: Uses lightweight TF-IDF for section ranking
✅ **Keyword Extraction**: Simple frequency-based keyword extraction
✅ **Smart Summarization**: Sentence scoring based on keyword presence
✅ **Persona-Driven**: Customizes output based on user role and goals
✅ **Fast Processing**: Optimized for <5 second processing time
✅ **Fully Offline**: No external dependencies or model downloads

## How It Works

1. **PDF Parsing**: Extracts text sections using PyMuPDF
2. **Section Detection**: Identifies headings based on font size, bold text, and keywords
3. **TF-IDF Ranking**: Uses scikit-learn's TF-IDF to rank sections by relevance
4. **Keyword Extraction**: Identifies important terms using frequency analysis
5. **Smart Summarization**: Selects sentences based on keyword density and length

## Customization

### Adding Keywords
Edit the `BOOST_KEYWORDS` list in `process.py` to prioritize specific terms.

### Changing Persona
Modify `persona.json` to match your research domain and goals.

### Output Format
The tool extracts:
- Top 5 most relevant sections
- Keywords for each section
- Summarized insights
- Page references for easy navigation
