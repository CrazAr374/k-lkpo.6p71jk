import os
import json
import fitz  # PyMuPDF
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import time
from collections import Counter

INPUT_DIR = "input"
PERSONA_FILE = "persona.json"
OUTPUT_DIR = "output"
OUTPUT_FILE = "result.json"

# Load persona and job
try:
    with open(PERSONA_FILE, "r", encoding="utf-8") as f:
        persona_data = json.load(f)

    persona = persona_data.get("persona", "")
    job = persona_data.get("job_to_be_done", "")
    if isinstance(persona, dict):
        persona = persona.get("role", "")
    if isinstance(job, dict):
        job = job.get("task", "")

    if not job:
        job = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks in computational biology"

    persona_job_text = f"{persona}. {job}"
except Exception as e:
    print(f"Error loading persona.json: {e}")
    persona = "PhD Researcher in Computational Biology"
    job = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
    persona_job_text = f"{persona}. {job}"

BOOST_KEYWORDS = [
    "methodology", "methodologies", "dataset", "datasets", "benchmark", "benchmarks",
    "model", "models", "algorithm", "algorithms", "experiment", "experiments",
    "results", "evaluation", "comparison", "literature review", "related work",
    "approach", "technique", "method", "framework", "system", "performance",
    "analysis", "implementation", "design", "architecture", "protocol",
    "fraud", "detection", "risk", "prediction", "finance", "transaction", "security", "profiling",
    "credit", "credit scoring", "fraud analytics", "compliance", "regulatory", "real-time monitoring"
]
BOOST_KEYWORDS_LOWER = [k.lower() for k in BOOST_KEYWORDS]

NOISE_TITLES = [
    "resume", "certificate", "cover page", "acknowledgement", "references", "bibliography", "index",
    "table of contents", "abstract", "appendix", "introduction", "student name"
]

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)

def extract_keywords(text, top_n=5):
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = set(["the", "is", "at", "which", "on", "and", "a", "an", "in", "for", "of", "to", "with", "this", "that"])
    words = [w for w in words if w not in stop_words and len(w) > 2]
    word_counts = Counter(words)
    boosted_words = []
    for word, count in word_counts.items():
        if word in BOOST_KEYWORDS_LOWER:
            boosted_words.extend([word] * count * 2)
        else:
            boosted_words.extend([word] * count)
    final_counts = Counter(boosted_words)
    return [word for word, _ in final_counts.most_common(top_n)]

def smart_sentence_split(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())

def extract_summary(text, num_sentences=2):
    try:
        sentences = smart_sentence_split(text)
    except:
        sentences = text.split('. ')
    sentences = [s.strip() for s in sentences if len(s.strip().split()) >= 10]  # Filter short entries
    if len(sentences) <= num_sentences:
        return sentences
    scored = []
    for sent in sentences:
        score = sum(1 for kw in BOOST_KEYWORDS_LOWER if kw in sent.lower())
        if 10 <= len(sent.split()) <= 30:
            score += 1
        if re.search(r'\d{4}', sent):
            score += 1
        scored.append((sent, score))
    scored.sort(key=lambda x: -x[1])
    return [s for s, _ in scored[:num_sentences]]

def extract_sections_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in BOOST_KEYWORDS_LOWER):
                if any(noise in line.lower() for noise in NOISE_TITLES):
                    continue
                title = line
                content = " ".join(lines[i+1:i+12])[:2000]
                sections.append({
                    "document": os.path.basename(pdf_path),
                    "page": page_num + 1,
                    "section_title": title,
                    "section_content": content
                })
                break
    return sections

def get_all_sections(input_dir):
    all_sections = []
    input_pdfs = []
    for fname in os.listdir(input_dir):
        if fname.lower().endswith(".pdf"):
            if any(x in fname.lower() for x in NOISE_TITLES):
                continue
            path = os.path.join(input_dir, fname)
            input_pdfs.append(fname)
            print(f"📄 {fname}")
            sections = extract_sections_from_pdf(path)
            all_sections.extend(sections)
    return all_sections, input_pdfs

def boost_score(section):
    score = 1.0
    title = section["section_title"].lower()
    content = section["section_content"].lower()
    for kw in BOOST_KEYWORDS_LOWER:
        if kw in title:
            score += 0.3
        if kw in content:
            score += 0.1
    return min(score, 2.0)

def rank_sections(sections, query):
    texts = [f"{s['section_title']} {s['section_content']}" for s in sections]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        query_vec = vectorizer.transform([query])
        sims = cosine_similarity(query_vec, tfidf_matrix)[0]
        for i, sec in enumerate(sections):
            sec["importance_rank"] = float(sims[i]) * boost_score(sec)
        return sorted([s for s in sections if s["importance_rank"] > 0.1], key=lambda x: -x["importance_rank"])
    except:
        for sec in sections:
            sec["importance_rank"] = boost_score(sec)
        return sorted([s for s in sections if s["importance_rank"] > 0.1], key=lambda x: -x["importance_rank"])

def make_output_json(pdfs, persona, job, sections):
    top = sections[:5]
    extracted = []
    analysis = []
    for idx, s in enumerate(top):
        summary = extract_summary(s["section_content"])
        keywords = extract_keywords(s["section_content"])
        sub = [{
            "rank": idx+1,
            "refined_text": sent,
            "document": s["document"],
            "page": s["page"]
        } for sent in summary]
        extracted.append({
            "document": s["document"],
            "page": s["page"],
            "section_title": s["section_title"],
            "importance_rank": round(s["importance_rank"], 3),
            "keywords": keywords,
            "summary": summary[0] if summary else "",
            "sub_sections": sub
        })
        analysis.extend(sub)
    return {
        "metadata": {
            "input_documents": pdfs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted,
        "subsection_analysis": analysis
    }

def main():
    start = time.time()
    all_sections, pdfs = get_all_sections(INPUT_DIR)
    if not all_sections:
        print("[!] No relevant sections found.")
        return
    ranked = rank_sections(all_sections, persona_job_text)
    result = make_output_json(pdfs, persona, job, ranked)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Output written to {output_path}")
    print(f"⏱️  Total processing time: {time.time() - start:.2f} seconds")
    print(f"📊 Extracted {len(result['extracted_sections'])} top sections")

if __name__ == "__main__":
    main()
