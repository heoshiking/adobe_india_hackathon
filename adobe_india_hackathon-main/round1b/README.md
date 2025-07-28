# Challenge 1B: Persona-Driven Multi-Collection PDF Intelligence
# AUTHOR -HARISH KUMAR , ARSHIT SINGLA
## 🧠 Overview
This project solves **Round 1B** of the Adobe India Hackathon 2025. The goal is to analyze multiple PDF document collections and extract meaningful sections tailored to a specific **persona** and their **job to be done** (JTBD).

The entire pipeline is containerized using **Docker** and processes all collections under the `input/` directory, generating structured `output.json` files inside `output/`.

---

## 📁 Project Structure

round1b/
├── input/
│ ├── collection1/
│ │ ├── input.json
│ │ ├── doc1.pdf ...
│ ├── collection2/
│ ├── collection3/
├── output/
│ ├── collection1/
│ │ └── output.json
│ ├── collection2/
│ ├── collection3/
├── main.py
├── Dockerfile
├── requirements.txt
└── README.md


---

## 💡 Collections Overview

### 🧳 Collection 1: Travel Planning
- **Challenge ID**: `round_1b_002`
- **Persona**: Travel Planner
- **Task**: Plan a 4-day trip to the South of France for 10 college friends
- **Input**: 7 Travel Guide PDFs

### 🧾 Collection 2: Acrobat Learning
- **Challenge ID**: `round_1b_003`
- **Persona**: HR Professional
- **Task**: Manage fillable onboarding & compliance forms
- **Input**: 15 Acrobat PDF Tutorials

### 🥗 Collection 3: Recipes
- **Challenge ID**: `round_1b_001`
- **Persona**: Food Contractor
- **Task**: Design vegetarian buffet for a corporate event
- **Input**: 9 Recipe PDFs

---

## 📥 Input JSON Format

```json
{
  "challenge_info": {
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case"
  },
  "documents": [
    { "filename": "doc.pdf", "title": "Title" }
  ],
  "persona": { "role": "User Persona" },
  "job_to_be_done": { "task": "Use case description" }
}
