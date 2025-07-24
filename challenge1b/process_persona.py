import fitz  # PyMuPDF
import json
import os
import re
from collections import defaultdict
from datetime import datetime

# --- Configuration ---
INPUT_DIR = '/input'
OUTPUT_DIR = '/output'
PERSONA_FILE = '/persona.json'  # Contains persona and job-to-be-done

# --- Helper Functions ---
def normalize_text(text):
    return re.sub(r'\s+', ' ', text.strip().lower())

def extract_headings(doc):
    headings = []
    sizes = defaultdict(int)
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:
                for line in block["lines"]:
                    line_text = " ".join(span['text'] for span in line['spans']).strip()
                    if not line_text:
                        continue
                    avg_size = sum(span['size'] * len(span['text']) for span in line['spans']) / sum(len(span['text']) for span in line['spans'])
                    sizes[round(avg_size)] += 1
                    headings.append({
                        'text': line_text,
                        'page': page_num,
                        'size': avg_size
                    })
    # Cluster font sizes for dynamic levels
    unique_sizes = sorted(list(set([round(h['size']) for h in headings])), reverse=True)
    size_map = {}
    for i, sz in enumerate(unique_sizes):
        size_map[sz] = f'H{i+1}'
    for h in headings:
        h['level'] = size_map.get(round(h['size']), 'H3')
    return headings

def rank_sections(headings, persona, job):
    # Simple keyword-based ranking for demo
    keywords = set(normalize_text(persona + ' ' + job).split())
    for h in headings:
        h['importance_rank'] = sum(1 for word in keywords if word in normalize_text(h['text']))
    ranked = sorted(headings, key=lambda x: -x['importance_rank'])
    return ranked

def process_documents(input_dir, persona, job):
    results = []
    for fname in os.listdir(input_dir):
        if not fname.lower().endswith('.pdf'):
            continue
        pdf_path = os.path.join(input_dir, fname)
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Failed to open {fname}: {e}")
            continue
        title = doc.metadata.get('title', fname.replace('.pdf', ''))
        headings = extract_headings(doc)
        ranked = rank_sections(headings, persona, job)
        # Top 10 sections for demo
        top_sections = ranked[:10]
        # Sub-section analysis: just take first 2 children for demo
        sub_sections = []
        for h in top_sections:
            sub_sections.append({
                'document': fname,
                'refined_text': h['text'],
                'page': h['page']
            })
        results.append({
            'document': fname,
            'title': title,
            'sections': top_sections,
            'sub_sections': sub_sections
        })
        doc.close()
    return results

def main():
    # Load persona and job-to-be-done
    if os.path.exists(PERSONA_FILE):
        with open(PERSONA_FILE, 'r', encoding='utf-8') as f:
            persona_data = json.load(f)
        persona = persona_data.get('persona', '')
        job = persona_data.get('job', '')
    else:
        persona = input('Enter persona description: ')
        job = input('Enter job-to-be-done: ')
    print(f"Persona: {persona}\nJob: {job}")
    results = process_documents(INPUT_DIR, persona, job)
    output = {
        'metadata': {
            'input_documents': [r['document'] for r in results],
            'persona': persona,
            'job_to_be_done': job,
            'processing_timestamp': datetime.now().isoformat()
        },
        'extracted_sections': [
            {
                'document': r['document'],
                'sections': r['sections'],
                'sub_sections': r['sub_sections']
            } for r in results
        ]
    }
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(os.path.join(OUTPUT_DIR, 'challenge1b_output.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print('Output written to challenge1b_output.json')

if __name__ == '__main__':
    main()
