import re
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path

def combine_state_files(state_path: Path, combined_path: Path, batch_size=30):
    combined_path.mkdir(exist_ok=True)
    def extract_number(file): return int(re.search(r'_(\d{6})\.pdf$', file.name)[1])
    files = sorted(state_path.glob('*.pdf'), key=extract_number)

    for i in range(0, len(files), batch_size):
        writer = PdfWriter()
        for file in files[i:i + batch_size]:
            reader = PdfReader(str(file))
            for page in reader.pages:
                writer.add_page(page)
        out_file = combined_path / f"combined_{i//batch_size + 1}.pdf"
        with open(out_file, 'wb') as f:
            writer.write(f)
