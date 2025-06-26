import re
from docx import Document
from PyPDF2 import PdfReader
from pathlib import Path

def find_docx(first, last, people_dirs):
    for d in people_dirs:
        doc_path = d / f"{first}_{last}.docx"
        if doc_path.exists():
            return doc_path
    return None

def create_envelope_docs(combined_path: Path, people_dirs, envelope_path: Path):
    envelope_path.mkdir(exist_ok=True)
    for combined_file in combined_path.glob('*.pdf'):
        reader = PdfReader(str(combined_file))
        doc = Document()
        for page in reader.pages:
            text = page.extract_text()
            match = re.search(r'([A-Z][a-z]+)\s([A-Z][a-z]+)', text)
            if match:
                first, last = match.groups()
                doc_path = find_docx(first, last, people_dirs)
                if doc_path:
                    d = Document(str(doc_path))
                    for elem in d.element.body:
                        doc.element.body.append(elem)
        doc.save(envelope_path / f"{combined_file.stem}.docx")
