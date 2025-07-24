# Document Outline Extraction Solution (Python)

This project is a high-performance, Docker-based, offline solution for extracting structured outlines from PDF documents using Python. It is designed to meet the requirements of the "Connecting the Dots" hackathon challenge.

## Approach

This solution uses the `PyMuPDF` library, renowned for its speed and accuracy, to ensure fast and reliable text extraction. The core of the solution is a Python script that intelligently identifies headings without relying on network-based AI models, adhering strictly to the offline constraint.

1.  **High-Performance Text & Font Analysis**: The script uses `PyMuPDF` to extract not just the text from each page, but also crucial metadata like font size and style (e.g., bold). This is far more reliable than plain text analysis.

2.  **Statistical Heading Detection**: Before processing, the script first analyzes the entire document to find the most common font size, which it determines to be the `body` text size. Any text significantly larger than this is considered a potential heading. This statistical approach makes the detection robust across different document styles.

3.  **Intelligent Filtering**: A set of heuristics (e.g., checking line length, capitalization, and looking for section numbering like "1.1" or "A.") is applied to filter out non-heading text, ensuring that elements like page numbers or short phrases are not mistakenly identified as headings.

4.  **Hierarchical Structuring**: Headings are classified into H1, H2, and H3 based on their relative font sizes. The script then builds a logical hierarchy, correctly nesting subheadings under their parent headings. It can also gracefully handle "orphan" headings by placing them logically in the outline.

5.  **Offline and Self-Contained**: All dependencies (`PyMuPDF`) are listed in `requirements.txt` and installed within the Docker container. The solution runs entirely on the CPU and has no network dependencies, making it fully compliant with the offline execution requirement.

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
