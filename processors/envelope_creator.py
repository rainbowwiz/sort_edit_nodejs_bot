from docx import Document
from pathlib import Path

def normalize_name(name):
    return name.strip().lower().replace(" ", "_")

def find_docx(first, last, people_dirs):
    target = normalize_name(f"{first}_{last}")
    for d in people_dirs:
        for file in d.glob("*.docx"):
            if normalize_name(file.stem) == target:
                return file
    return None

def copy_doc_content(source_doc, target_doc):
    for para in source_doc.paragraphs:
        new_para = target_doc.add_paragraph()
        new_para.style = para.style
        for run in para.runs:
            new_run = new_para.add_run(run.text)
            new_run.bold = run.bold
            new_run.italic = run.italic
            new_run.underline = run.underline
            new_run.font.name = run.font.name
            new_run.font.size = run.font.size

def create_envelope_docs(combined_path: Path, people_dirs, all_name_lists, envelope_path: Path):
    envelope_path.mkdir(exist_ok=True)
    combined_files = sorted(combined_path.glob('*.pdf'))

    for idx, combined_file in enumerate(combined_files):
        doc = Document()
        name_list = all_name_lists[idx]

        for i, (last, first) in enumerate(name_list):
            doc_path = find_docx(first, last, people_dirs)
            if doc_path:
                person_doc = Document(str(doc_path))
                copy_doc_content(person_doc, doc)
                if i < len(name_list) - 1:
                    doc.add_page_break()
            else:
                print(f"⚠️ No docx found for: {first} {last}")

        output_filename = f"{combined_file.stem}.docx"
        doc.save(envelope_path / output_filename)
        print(f"📄 Saved envelope: {output_filename}")
