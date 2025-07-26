# Document Outline Extraction Solution (Python)

This project is a high-performance, Docker-based, offline solution for extracting structured outlines from PDF documents using Python. It is designed to meet the requirements of the "Connecting the Dots" hackathon challenge.

## Approach

This solution uses the `PyMuPDF` library, renowned for its speed and accuracy, to ensure fast and reliable text extraction. The core of the solution is a Python script that intelligently identifies headings without relying on network-based AI models, adhering strictly to the offline constraint.

### Key Features (v2)

1.  **Weighted, Multilingual Heading Detection**: The script uses a composite scoring system for each line, considering font size, boldness, centering, section patterns, and multilingual heading keywords (English, Spanish, French, Hindi, and more). This ensures robust detection across diverse document styles and languages.

2.  **Statistical Font Analysis**: The script analyzes the entire document to find the most common font size (body text baseline). Heading levels (H1, H2, H3) are assigned by clustering font sizes relative to this baseline, making the detection adaptive to each PDF.

3.  **Intelligent Filtering & Deduplication**: Heuristics filter out non-headings (e.g., page numbers, short/long lines, lines ending with periods). Headings are deduplicated by normalized text, and only the first occurrence is kept.

4.  **Improved Title Extraction**: The script uses a 3-tier fallback: (1) PDF metadata, (2) largest font text on page 1, (3) centered bold text in the top 20% of page 1, and finally falls back to "Untitled Document" if needed.

5.  **Flat Outline Output**: The output is a flat list of headings (not nested), each with its level (H1, H2, H3), text, and page number, matching the required format.

6.  **Multilingual & Unicode Support**: All text is normalized using Unicode standards, and output JSON is written with `ensure_ascii=False` to preserve all characters.

7.  **Offline and Self-Contained**: All dependencies (`PyMuPDF`) are listed in `requirements.txt` and installed within the Docker container. The solution runs entirely on the CPU and has no network dependencies, making it fully compliant with the offline execution requirement.

## Output Format

Example output for a PDF:

```
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

## How to Build and Run

### Build the Docker Image

Use the following command in your terminal at the root of the `doc_new1` directory. This command builds your Docker image with the name `neurolense-solution`.

```sh
docker build -t neurolense-solution .
```
*Note: The provided `Dockerfile` explicitly specifies the `--platform=linux/amd64` to ensure compatibility, as per the hackathon requirements.*

### Run the Solution

1.  Create a local directory for your input PDF files (e.g., `my_input_pdfs`).
2.  Create an empty local directory for the JSON output (e.g., `my_output_jsons`).
3.  Place all the PDFs you want to process into the input directory you created.

Then, run the container using the following command. **Make sure to replace the placeholder paths with the absolute paths** to your input and output directories.

```sh
docker run --rm \
  -v "/path/to/your/my_input_pdfs":/app/input \
  -v "/path/to/your/my_output_jsons":/app/output \
  neurolense-solution
```

The container will automatically process each PDF in the input folder and generate a corresponding `.json` file in the output folder.
