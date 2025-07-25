import os
import json
import fitz  # PyMuPDF
import re
import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from keybert import KeyBERT
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from datetime import datetime

nltk.download('punkt', quiet=True)

INPUT_DIR = "input"
OUTPUT_DIR = "output"
PERSONA_FILE = "persona.json"
OUTPUT_FILE = "result.json"

with open(PERSONA_FILE, "r", encoding="utf-8") as f:
    persona_data = json.load(f)
persona = persona_data.get("persona", "")
job = persona_data.get("job", "")
persona_job_text = f"{persona}. {job}"

BOOST_KEYWORDS = [
    "methodology", "methodologies", "dataset", "datasets", "benchmark", "benchmarks",
    "computational biology", "introduction", "methods", "results", "discussion", "conclusion"
]
BOOST_KEYWORDS_LOWER = [k.lower() for k in BOOST_KEYWORDS]

# Load MiniLM model and KeyBERT
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
kw_model = KeyBERT(model)


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text

def extract_sections_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    line_text = " ".join(span["text"] for span in line["spans"])
                    line_text = clean_text(line_text)
                    if len(line_text) < 20:
                        continue  # skip very short lines
                    avg_size = np.mean([span["size"] for span in line["spans"]])
                    if avg_size >= 13:
                        section_title = line_text
                        section_content = []
                        found_heading = False
                        for next_block in blocks:
                            if next_block == block:
                                found_heading = True
                                continue
                            if not found_heading:
                                continue
                            for next_line in next_block.get("lines", []):
                                next_text = " ".join(span["text"] for span in next_line["spans"])
                                next_text = clean_text(next_text)
                                if len(next_text) < 10:
                                    continue
                                if any(word in next_text.lower() for word in BOOST_KEYWORDS_LOWER) and len(next_text.split()) < 10:
                                    break
                                section_content.append(next_text)
                            if section_content:
                                break
                        full_section = {
                            "document": os.path.basename(pdf_path),
                            "page": page_num,
                            "section_title": section_title,
                            "section_content": " ".join(section_content)[:2000]
                        }
                        sections.append(full_section)
    doc.close()
    return sections

def get_all_sections(input_dir):
    all_sections = []
    input_pdfs = []
    for fname in os.listdir(input_dir):
        if fname.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, fname)
            input_pdfs.append(fname)
            sections = extract_sections_from_pdf(pdf_path)
            all_sections.extend(sections)
    return all_sections, input_pdfs

def extract_keywords(text, top_n=5):
    try:
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
        return [kw for kw, _ in keywords]
    except Exception:
        return []

def extract_summary(text, num_sentences=2):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        summary = summarizer(parser.document, num_sentences)
        return " ".join(str(sentence) for sentence in summary)
    except Exception:
        return ""

def boost_score(section):
    title = section["section_title"].lower()
    content = section["section_content"].lower()
    for kw in BOOST_KEYWORDS_LOWER:
        if kw in title or kw in content:
            return 1.5
    return 1.0

def rank_sections(sections, persona_job_text):
    section_texts = [f"{s['section_title']}. {s['section_content']}" for s in sections]
    query_emb = model.encode([persona_job_text])
    section_embs = model.encode(section_texts)
    sims = cosine_similarity(query_emb, section_embs)[0]
    for i, s in enumerate(sections):
        boost = boost_score(s)
        s["importance_rank"] = float(sims[i]) * boost
    ranked = sorted(sections, key=lambda x: -x["importance_rank"])
    return ranked

def make_output_json(input_pdfs, persona, job, ranked_sections, persona_job_text):
    top_sections = ranked_sections[:10]
    global_summary_parts = []
    for s in top_sections:
        s["keywords"] = extract_keywords(s["section_content"], top_n=5)
        s["summary"] = extract_summary(s["section_content"], num_sentences=2)
        if boost_score(s) > 1.0 and s["summary"]:
            global_summary_parts.append(f"[{s['section_title']}] (keywords: {', '.join(s['keywords'])}): {s['summary']}")
    if global_summary_parts:
        global_summary = (
            f"For persona '{persona}' (goal: {job}), the most relevant sections related to methodologies, datasets, benchmarks, and computational biology are: "
            + " ".join(global_summary_parts)
        )
    else:
        global_summary = (
            f"For persona '{persona}' (goal: {job}), no highly relevant sections on methodologies, datasets, benchmarks, or computational biology were found."
        )
    output = {
        "metadata": {
            "input_documents": input_pdfs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "global_summary": global_summary,
        "extracted_sections": [
            {
                "document": s["document"],
                "page": s["page"],
                "section_title": s["section_title"],
                "importance_rank": s["importance_rank"],
                "keywords": s["keywords"],
                "summary": s["summary"]
            }
            for s in top_sections
        ]
    }
    return output

def main():
    all_sections, input_pdfs = get_all_sections(INPUT_DIR)
    if not all_sections:
        print("No sections found in input PDFs.")
        return
    ranked_sections = rank_sections(all_sections, persona_job_text)
    output_json = make_output_json(input_pdfs, persona, job, ranked_sections, persona_job_text)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, OUTPUT_FILE), "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)
    print(f"Output written to {os.path.join(OUTPUT_DIR, OUTPUT_FILE)}")

if __name__ == "__main__":
    main()
