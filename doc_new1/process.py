import fitz  # PyMuPDF
import json
import os
import re
from operator import itemgetter
from collections import defaultdict

# --- Configuration ---
INPUT_DIR = '/input'
OUTPUT_DIR = '/output'
# --- Helper Functions ---
def normalize_text(text):
    return re.sub(r'\s+', ' ', text.strip().lower())

def is_symbolic(text):
    return re.match(r'^[^\w]+$', text)

def is_section_number(text):
    return re.match(r'^(\d+(\.\d+)*|[A-Z]\.)', text)

# --- Heuristics for Heading Detection ---
# Identify headings based on font size and style.
# We'll calculate a 'score' for each line to determine if it's a heading.

def get_line_stats(doc):
    """
    Analyzes the entire document to find statistics about text sizes,
    which helps in differentiating headings from body text more reliably.
    """
    sizes = defaultdict(int)
    total_chars = 0
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = round(span['size'])
                        sizes[font_size] += len(span['text'].strip())
                        total_chars += len(span['text'].strip())
    
    if not sizes:
        return 0, 0

    # Find the most common font size (likely body text)
    body_size = max(sizes, key=sizes.get)
    
    # Set a threshold for what we consider a heading
    heading_threshold = body_size + 1
    
    return body_size, heading_threshold, None


def is_likely_heading(line):
    """
    Checks if a line of text is likely to be a heading.
    - Short length
    - Ends with no punctuation (or specific allowed punctuation)
    - Not just numbers
    """
    text = line['text'].strip()
    if len(text) < 3 or len(text) > 150:
        return False
    if text.endswith('.') and not any(text.endswith(x) for x in ['...', 'etc.']):
        return False
    if text.isdigit(): # Exclude page numbers
        return False
    # Simple check for title case or all caps
    if text.istitle() or text.isupper():
        return True
    # Check for section numbering (e.g., "1.1", "A.")
    if re.match(r'^\s*(\d{1,2}(\.\d{1,2})*\.?|\w\.)\s', text):
        return True
    return False

def build_outline(doc, body_size, heading_threshold):
    """Builds a hierarchical outline from the document."""
    outline = []
    
    # This list will hold all identified potential headings
    potential_headings = []

    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block["lines"]:
                    # Heuristic: combine spans to reconstruct the line's text and get avg size
                    line_text = " ".join(span['text'] for span in line['spans']).strip()
                    if not line_text:
                        continue

                    avg_size = sum(span['size'] * len(span['text']) for span in line['spans']) / sum(len(span['text']) for span in line['spans'])
                    
                    if avg_size >= heading_threshold and is_likely_heading({'text': line_text}):
                        potential_headings.append({
                            'text': line_text,
                            'page': page_num,
                            'size': avg_size
                        })

    if not potential_headings:
        return []

    # Identify the top-level heading sizes (e.g., H1 size, H2 size)
    unique_sizes = sorted(list(set([h['size'] for h in potential_headings])), reverse=True)
    
    size_map = {}
    if len(unique_sizes) > 0:
        size_map[unique_sizes[0]] = 'H1'
    if len(unique_sizes) > 1:
        size_map[unique_sizes[1]] = 'H2'
    if len(unique_sizes) > 2:
        size_map[unique_sizes[2]] = 'H3'

    # Assign H1, H2, H3 based on font size
    headings = []
    for h in potential_headings:
        level = size_map.get(h['size'], 'H3') # Default to H3 if size not in top 2
        headings.append({'level': level, 'text': h['text'], 'page': h['page']})

    # Build hierarchy
    structured_outline = []
    path = [None, None] # Path to current H1, H2

    for h in headings:
        level_index = int(h['level'][-1]) - 1

        if level_index == 0: # H1
            item = {'level': 'H1', 'text': h['text'], 'page': h['page'], 'children': []}
            structured_outline.append(item)
            path[0] = item
            path[1] = None
        elif level_index == 1: # H2
            item = {'level': 'H2', 'text': h['text'], 'page': h['page'], 'children': []}
            if path[0]:
                path[0]['children'].append(item)
            else: # Orphan H2, create a dummy H1
                dummy_h1 = {'level': 'H1', 'text': 'Miscellaneous', 'page': h['page'], 'children': [item]}
                structured_outline.append(dummy_h1)
                path[0] = dummy_h1
            path[1] = item
        elif level_index == 2: # H3
            item = {'level': 'H3', 'text': h['text'], 'page': h['page']}
            if path[1]: # Attach to H2
                path[1]['children'].append(item)
            elif path[0]: # Or attach to H1
                path[0]['children'].append(item)
    
    # Clean up empty children arrays
    def clean_children(items):
        for item in items:
            if 'children' in item:
                if item['children']:
                    clean_children(item['children'])
                else:
                    del item['children']
    
    clean_children(structured_outline)
    return structured_outline

    # Advanced heading extraction
    headings = []
    seen = set()
    heading_freq = defaultdict(int)
    font_sizes = []
    font_styles = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block["lines"]:
                    line_text = " ".join(span['text'] for span in line['spans']).strip()
                    if not line_text:
                        continue
                    avg_size = sum(span['size'] * len(span['text']) for span in line['spans']) / sum(len(span['text']) for span in line['spans'])
                    font_flags = max([span.get('flags', 0) for span in line['spans']])
                    is_bold = bool(font_flags & 2)
                    x0 = min([span.get('origin', (0,0))[0] if 'origin' in span else 0 for span in line['spans']])
                    key = (normalize_text(line_text), page_num)
                    if avg_size >= heading_threshold and is_likely_heading({'text': line_text}):
                        # Reduce duplicates
                        if key in seen:
                            continue
                        seen.add(key)
                        heading_freq[normalize_text(line_text)] += 1
                        font_sizes.append(avg_size)
                        font_styles.append(is_bold)
                        headings.append({
                            'text': line_text,
                            'page': page_num,
                            'size': avg_size,
                            'bold': is_bold,
                            'x': x0
                        })
    # Filter out headings that repeat too often (likely headers/footers)
    filtered_headings = [h for h in headings if heading_freq[normalize_text(h['text'])] < 3]
    if not filtered_headings:
        return []
    # Cluster font sizes for dynamic levels
    unique_sizes = sorted(list(set([round(h['size']) for h in filtered_headings])), reverse=True)
    size_map = {}
    for i, sz in enumerate(unique_sizes):
        size_map[sz] = f'H{i+1}'
    # Assign levels
    for h in filtered_headings:
        h['level'] = size_map.get(round(h['size']), 'H3')
    # Build hierarchy using stack
    outline = []
    stack = []
    for h in filtered_headings:
        item = {
            'level': h['level'],
            'text': h['text'],
            'page': h['page'],
            'bold': h['bold'],
            'x': h['x'],
            'size': h['size'],
            'children': [],
            'section': None
        }
        # Section number extraction
        m = re.match(r'^(\d+(\.\d+)*|[A-Z]\.)', h['text'])
        if m:
            item['section'] = m.group(0)
        # Find parent in stack
        while stack and stack[-1]['level'] >= item['level']:
            stack.pop()
        if stack:
            stack[-1]['children'].append(item)
        else:
            outline.append(item)
        stack.append(item)
    # Clean up empty children arrays
    def clean_children(items):
        for item in items:
            if 'children' in item:
                if item['children']:
                    clean_children(item['children'])
                else:
                    del item['children']
    clean_children(outline)
    return outline

def process_pdf(pdf_path):
    """Main processing function for a single PDF file."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"  -> Failed to open {os.path.basename(pdf_path)}: {e}")
        return None

    # Try to get title from metadata, otherwise use filename
    title = doc.metadata.get('title', os.path.basename(pdf_path).replace('.pdf', ''))
    if not title:
        title = "Untitled Document"

    body_size, heading_threshold, _ = get_line_stats(doc)
    if body_size == 0:
        print(f"  -> Could not determine body font size for {os.path.basename(pdf_path)}. Skipping.")
        return None
        
    outline = build_outline(doc, body_size, heading_threshold)
    
    doc.close()

    return {"title": title, "outline": outline}

def main():
    """Main loop to process all PDFs in the input directory."""
    print(f"Starting document processing in {INPUT_DIR}")
    
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' does not exist.")
        return
        
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print('No PDF files found in /app/input. Exiting.')
        return

    print(f"Found {len(pdf_files)} PDF(s) to process.")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for pdf_file in pdf_files:
        input_path = os.path.join(INPUT_DIR, pdf_file)
        output_filename = f"{os.path.splitext(pdf_file)[0]}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        print(f"Processing: {pdf_file}...")
        
        result = process_pdf(input_path)
        
        if result:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"  -> Successfully generated {output_filename}")
            except Exception as e:
                print(f"  -> Failed to write JSON for {pdf_file}: {e}")

    print('All files processed. Shutting down.')

if __name__ == '__main__':
    main()
