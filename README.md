# adobe_india_hackathon
# 🧠 PDF Intelligence System – Hackathon Submission (Adobe India 2025)

This repository contains our complete solution to the **Adobe India Hackathon 2025**, featuring:

- **Round 1A** – PDF Outline Extraction System
- **Round 1B** – Persona-Driven Multi-Collection PDF Intelligence

---

## 📁 Folder Structure


---

## ✅ Round 1A – PDF Outline Extraction System

This module processes PDF files to extract structured outlines and heading levels (H1, H2, H3), saving results in a clean JSON format.

### ✨ Features
- Supports native text PDFs and OCR (for scanned files)
- Identifies headings using font size, position, and formatting patterns
- Outputs structured JSON outlines
- Fast processing (< 10 seconds per file)
- Customizable run modes and logs

### 📦 How to Use

1. Place your PDFs inside: `round1a/input/`
2. Run one of the following from the `round1a/` directory:
   ```bash
   python main.py                   # Simple run
   python run.py                    # Recommended
   python run.py --verbose          # Detailed logging
   python run.py --summary          # Summary report only
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
round1b/
├── input/
│   ├── collection1/
│   │   ├── input.json
│   │   ├── doc1.pdf ...
│   ├── collection2/
│   ├── collection3/
├── output/
│   ├── collection1/output.json
│   ├── collection2/
│   ├── collection3/
├── main.py
├── Dockerfile
├── requirements.txt
└── README.md
{
  "challenge_info": {
    "challenge_id": "round_1b_002",
    "test_case_name": "trip_planner_case"
  },
  "documents": [
    { "filename": "doc1.pdf", "title": "France Travel Guide" }
  ],
  "persona": { "role": "Travel Planner" },
  "job_to_be_done": { "task": "Plan a 4-day trip for 10 friends to South of France" }
}

cd round1b/
docker build -t round1b-pdf .
docker run -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" round1b-pdf
