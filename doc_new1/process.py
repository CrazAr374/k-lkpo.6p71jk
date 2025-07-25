import fitz  # PyMuPDF
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

# --- Configuration ---
INPUT_DIR = '/input'
OUTPUT_DIR = '/output'

# --- Multilingual Heading Keywords ---
HEADING_KEYWORDS = {
    'english': ['chapter', 'section', 'part', 'introduction', 'conclusion', 'summary', 'profile', 'education', 'experience', 'skills', 'projects', 'certifications', 'interests', 'languages', 'contact'],
    'spanish': ['capítulo', 'sección', 'parte', 'introducción', 'conclusión', 'resumen', 'perfil', 'educación', 'experiencia', 'habilidades', 'proyectos', 'certificaciones', 'intereses', 'idiomas', 'contacto'],
    'french': ['chapitre', 'section', 'partie', 'introduction', 'conclusion', 'résumé', 'profil', 'éducation', 'expérience', 'compétences', 'projets', 'certifications', 'intérêts', 'langues', 'contact'],
    'hindi': ['अध्याय', 'खंड', 'भाग', 'परिचय', 'निष्कर्ष', 'सारांश', 'प्रोफ़ाइल', 'शिक्षा', 'अनुभव', 'कौशल', 'परियोजनाएँ', 'प्रमाणपत्र', 'रुचियाँ', 'भाषाएँ', 'संपर्क'],
    # Add more as needed
}

# --- Helper Functions ---
def normalize_text(text):
    text = unicodedata.normalize('NFKC', text)
    return re.sub(r'\s+', ' ', text.strip().lower())

def is_centered(span, page_width):
    x0 = span['bbox'][0]
    x1 = span['bbox'][2]
    center = (x0 + x1) / 2
    return abs(center - page_width / 2) < page_width * 0.15

def get_line_features(line, page_width):
    # Aggregate features for a line
    line_text = ' '.join(span['text'] for span in line['spans']).strip()
    sizes = [span['size'] for span in line['spans'] if span['text'].strip()]
    flags = [span.get('flags', 0) for span in line['spans'] if span['text'].strip()]
    bboxes = [span['bbox'] for span in line['spans'] if span['text'].strip()]
    colors = [span.get('color', 0) for span in line['spans'] if span['text'].strip()]
    underlined = any((span.get('flags', 0) & 4) for span in line['spans'] if span['text'].strip())
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    is_bold = any(f & 2 for f in flags)
    centered = all(is_centered({'bbox': bbox}, page_width) for bbox in bboxes) if bboxes else False
    y_pos = min(bbox[1] for bbox in bboxes) if bboxes else 0
    is_all_caps = line_text.isupper() and len(line_text) > 2
    color_val = max(colors) if colors else 0
    return {
        'text': line_text,
        'size': avg_size,
        'bold': is_bold,
        'centered': centered,
        'underlined': underlined,
        'color': color_val,
        'y': y_pos,
        'all_caps': is_all_caps
    }

def heading_score_hybrid(features, body_font_size, page_width):
    text = normalize_text(features['text'])
    size = features['size']
    bold = features['bold']
    centered = features['centered']
    underlined = features['underlined']
    color = features['color']
    y = features['y']
    all_caps = features['all_caps']
    score = 0.0
    # Font size weight
    if size >= body_font_size * 1.5:
        score += 1.0
    elif size >= body_font_size * 1.25:
        score += 0.7
    elif size > body_font_size:
        score += 0.4
    # Bold weight
    if bold:
        score += 0.3
    # Centered weight
    if centered:
        score += 0.2
    # Underlined weight
    if underlined:
        score += 0.2
    # All-caps weight
    if all_caps:
        score += 0.2
    # Colored (not black) weight
    if color > 0:
        score += 0.1
    # Pattern match (section numbers, roman numerals, bullets)
    if re.match(r'^(\d+(\.\d+)*|[A-Z]\.|[IVXLCDM]+\.|●|•)', text):
        score += 0.3
    # Multilingual keyword match
    first_word = text.split(' ')[0]
    for words in HEADING_KEYWORDS.values():
        if any(first_word.startswith(word) for word in words):
            score += 0.3
            break
    # Short heading allowance
    if 2 <= len(text) <= 20:
        score += 0.2
    # Length penalty
    if len(text) < 2 or len(text) > 150:
        score -= 1.0
    # End punctuation penalty
    if text.endswith('.') and not text.endswith('...'):
        score -= 0.5
    # Page number penalty
    if text.isdigit():
        score -= 1.0
    return score

def extract_title(doc):
    # 1. Try metadata
    title = doc.metadata.get('title', '').strip()
    if title:
        return title
    # 2. Largest font text on page 1
    page = doc[0]
    blocks = page.get_text('dict')['blocks']
    candidates = []
    page_width = page.rect.width
    for block in blocks:
        if block['type'] == 0:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if text:
                        candidates.append({'text': text, 'size': span['size'], 'bold': bool(span.get('flags', 0) & 2), 'centered': is_centered(span, page_width), 'y': span['bbox'][1]})
    if candidates:
        # Prefer largest font, then topmost, then centered bold
        candidates.sort(key=lambda x: (-x['size'], x['y']))
        # Try centered bold in top 20% of page
        top_20 = page.rect.height * 0.2
        for c in candidates:
            if c['centered'] and c['bold'] and c['y'] < top_20:
                return c['text']
        # Else largest font
        return candidates[0]['text']
    # 3. Fallback: filename
    return 'Untitled Document'

def get_body_font_size(doc):
    font_sizes = []
    for page in doc:
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if text:
                            font_sizes.append(round(span['size']))
    if not font_sizes:
        return 12  # fallback
    return Counter(font_sizes).most_common(1)[0][0]

def extract_headings(doc, body_font_size, parse_everything=False):
    headings = []
    seen = set()
    all_lines = []
    for page_num, page in enumerate(doc, 1):
        page_width = page.rect.width
        blocks = page.get_text('dict')['blocks']
        page_candidates = []
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    features = get_line_features(line, page_width)
                    features['page'] = page_num
                    score = heading_score_hybrid(features, body_font_size, page_width)
                    features['score'] = score
                    all_lines.append(features)
                    if score >= 0.5:
                        norm = normalize_text(features['text'])
                        key = (norm, page_num)
                        if key in seen:
                            continue
                        seen.add(key)
                        heading = dict(features)
                        headings.append(heading)
                        page_candidates.append(heading)
        # Fallback: if no headings detected on this page, add the largest text line as H3
        if not page_candidates:
            largest = None
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        features = get_line_features(line, page_width)
                        if not features['text']:
                            continue
                        if not largest or features['size'] > largest['size']:
                            largest = dict(features)
                            largest['page'] = page_num
                            largest['score'] = 0.0
            if largest:
                norm = normalize_text(largest['text'])
                key = (norm, page_num)
                if key not in seen:
                    seen.add(key)
                    headings.append(largest)
    if parse_everything:
        # Output all lines with their features for manual review
        return all_lines
    if not headings:
        return []
    # Deduplicate by normalized text (keep first occurrence)
    dedup = {}
    for h in headings:
        norm = normalize_text(h['text'])
        if norm not in dedup:
            dedup[norm] = h
    headings = list(dedup.values())
    # Assign levels by clustering font sizes
    sizes = [round(h['size']) for h in headings]
    if not sizes:
        return []
    unique_sizes = sorted(list(set(sizes)), reverse=True)
    size_map = {}
    if len(unique_sizes) > 0:
        size_map[unique_sizes[0]] = 'H1'
    if len(unique_sizes) > 1:
        size_map[unique_sizes[1]] = 'H2'
    if len(unique_sizes) > 2:
        size_map[unique_sizes[2]] = 'H3'
    for h in headings:
        h['level'] = size_map.get(round(h['size']), 'H3')
        h['children'] = []
    headings.sort(key=lambda h: (h['page'], h['y']))
    outline = []
    last_h1 = None
    last_h2 = None
    for h in headings:
        if h['level'] == 'H1':
            outline.append(h)
            last_h1 = h
            last_h2 = None
        elif h['level'] == 'H2':
            if last_h1:
                last_h1['children'].append(h)
            else:
                outline.append(h)
            last_h2 = h
        elif h['level'] == 'H3':
            if last_h2:
                last_h2['children'].append(h)
            elif last_h1:
                last_h1['children'].append(h)
            else:
                outline.append(h)
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
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"  -> Failed to open {os.path.basename(pdf_path)}: {e}")
        return None
    title = extract_title(doc)
    body_font_size = get_body_font_size(doc)
    parse_everything = os.environ.get('PARSE_EVERYTHING', '0') == '1'
    outline = extract_headings(doc, body_font_size, parse_everything=parse_everything)
    doc.close()
    if parse_everything:
        return {"title": title, "lines": outline}
    else:
        return {"title": title, "outline": outline}

def main():
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
