# 🧠 Adobe India Hackathon 2025 – Round 1 Submission

Welcome to our submission for Adobe India Hackathon 2025.  
This repository contains complete implementations for:

✅ **Round 1A:** PDF Outline Extraction  
✅ **Round 1B:** Persona-Driven Document Intelligence  

Both solutions are **Dockerized**, well-structured, and adhere to the challenge specifications.

---

## 📁 Repository Structure

adobe-hackathon-2025/
├── round1a/ # Round 1A – PDF Outline Extractor
│ ├── input/ # Input PDFs
│ ├── output/ # Output JSONs
│ ├── main.py # Outline extraction script
│ ├── Dockerfile
│ ├── requirements.txt
│ └── README.md
│
├── round1b/ # Round 1B – Multi-Collection Analysis
│ ├── Collection 1/ # Travel Planning
│ ├── Collection 2/ # Acrobat Learning
│ ├── Collection 3/ # Recipe Compilation
│ ├── main.py # Persona-driven analyzer
│ ├── Dockerfile
│ ├── requirements.txt
│ └── README.md
│
└── README.md # Root README (this file)


---

## 🔹 Round 1A – PDF Outline Extractor

### 🎯 Objective
Extract structured outlines (H1, H2, H3) from PDFs based on font size.

### 💡 Approach
- Use **PyMuPDF (fitz)** to parse PDF content.
- Classify headings by font size:
  - **H1 ≥ 16**
  - **H2 ≥ 13**
  - **H3 ≥ 11**
- Output structured JSON with title and outline.

### 🧪 Input & Output Format

📥 **Input** → PDFs placed in `round1a/input/`  
📤 **Output JSON** (saved in `round1a/output/`):

```json
{
  "title": "file01",
  "outline": [
    { "level": "H1", "text": "Main Heading", "page": 1 },
    { "level": "H2", "text": "Subheading", "page": 2 }
  ]
}
```
## 🔹 Round 1B – Persona-Driven Document Intelligence

### 🎯 Objective
Extract relevant content from a set of documents tailored to:

- A given persona (e.g., Travel Planner, HR Professional)  
- A specific job to be done (e.g., Plan a trip, Create forms)

### 📦 Collections

| Collection   | Challenge ID   | Persona         | Task Description                                  |
| ------------ | -------------- | --------------- | ------------------------------------------------- |
| Collection 1 | round_1b_002   | Travel Planner  | Plan a 4-day trip to South of France              |
| Collection 2 | round_1b_003   | HR Professional | Create/manage fillable onboarding forms           |
| Collection 3 | round_1b_001   | Food Contractor | Prepare vegetarian buffet for corporate gathering |

### 📥 Input JSON Format

```json
{
  "challenge_info": {
    "challenge_id": "round_1b_002",
    "test_case_name": "travel_planning"
  },
  "documents": [{ "filename": "guide.pdf", "title": "France Travel Guide" }],
  "persona": { "role": "Travel Planner" },
  "job_to_be_done": { "task": "Plan a 4-day trip" }
}
```
### 📥 Output JSON Format

```json
{
  "metadata": {
    "input_documents": ["guide.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a 4-day trip"
  },
  "extracted_sections": [
    {
      "document": "guide.pdf",
      "section_title": "Day 1 Itinerary",
      "importance_rank": 1,
      "page_number": 3
    },
    {
      "document": "guide.pdf",
      "section_title": "Day 2 Attractions",
      "importance_rank": 2,
      "page_number": 4
    }
  ],
  "subsection_analysis": [
    {
      "document": "guide.pdf",
      "refined_text": "Visit Nice and explore old town markets.",
      "page_number": 3
    },
    {
      "document": "guide.pdf",
      "refined_text": "Day 2 includes a tour of Cannes and Antibes.",
      "page_number": 4
    }
  ]
}
```
