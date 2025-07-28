import os
import json
import fitz  # PyMuPDF

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    outline = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = " ".join([span["text"] for span in line["spans"]]).strip()
                font_size = line["spans"][0]["size"]

                if font_size >= 16:
                    level = "H1"
                elif font_size >= 13:
                    level = "H2"
                elif font_size >= 11:
                    level = "H3"
                else:
                    continue

                outline.append({
                    "level": level,
                    "text": text,
                    "page": page_num + 1
                })

    return outline

def process_collection(collection_path, output_path):
    input_json = os.path.join(collection_path, "input.json")
    with open(input_json, encoding="utf-8") as f:
        job_info = json.load(f)

    documents = job_info["documents"]
    persona = job_info["persona"]["role"]
    task = job_info["job_to_be_done"]["task"]

    extracted_sections = []
    subsection_analysis = []

    for doc in documents:
        filename = doc["filename"]
        title = doc["title"]
        pdf_path = os.path.join(collection_path, filename)
        outline = extract_outline(pdf_path)

        for rank, section in enumerate(outline, 1):
            extracted_sections.append({
                "document": filename,
                "section_title": section["text"],
                "importance_rank": rank,
                "page_number": section["page"]
            })
            subsection_analysis.append({
                "document": filename,
                "refined_text": section["text"],
                "page_number": section["page"]
            })

    final_output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in documents],
            "persona": persona,
            "job_to_be_done": task
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

def main():
    input_root = "input"
    output_root = "output"

    for collection in os.listdir(input_root):
        collection_path = os.path.join(input_root, collection)
        output_path = os.path.join(output_root, collection, "output.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        process_collection(collection_path, output_path)

if __name__ == "__main__":
    main()
