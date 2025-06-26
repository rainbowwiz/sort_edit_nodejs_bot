import re
import random
import string
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path


def extract_name_from_second_page(pdf_path: Path):
    """Extract full name from the second page of an STFCS file."""
    try:
        reader = PdfReader(str(pdf_path))
        if len(reader.pages) >= 2:
            text = reader.pages[1].extract_text()
            # Look for a pattern like "Instructions to Mail ... for: BILAL ABDULLAH"
            match = re.search(r'for:\s+([A-Z][A-Za-z]+)\s+([A-Z][A-Za-z]+)', text, re.IGNORECASE)
            if match:
                return match.group(1).strip(), match.group(2).strip()
    except Exception as e:
        print(f"❌ Error reading {pdf_path.name}: {e}")
    return None


def generate_random_filename(first: str, last: str) -> str:
    """Generate a random 6-digit filename based on the name."""
    rand_digits = ''.join(random.choices(string.digits, k=6))
    return f"{last}_{first}_{rand_digits}.pdf"


def attach_w2_to_stfcs(company_path: Path, w2_path: Path, state_path: Path):
    """Attach W2 page to STFCS file after stripping first 2 pages."""
    state_path.mkdir(exist_ok=True)

    for subfolder in sorted(company_path.iterdir()):
        if not subfolder.is_dir():
            continue

        for file in sorted(subfolder.glob('STFCS*.pdf')):
            name = extract_name_from_second_page(file)
            if not name:
                print(f"⚠️ Could not extract name from: {file.name}")
                continue

            first, last = name
            first_lower = first.lower()
            last_lower = last.lower()
            matched_w2 = None

            # Search for matching W2 file (first match wins)
            for w2_file in sorted(w2_path.glob('*.pdf')):
                try:
                    reader = PdfReader(str(w2_file))
                    for page in reader.pages:
                        text = (page.extract_text() or "").lower()
                        if first_lower in text and last_lower in text:
                            matched_w2 = w2_file
                            break
                    if matched_w2:
                        break
                except Exception as e:
                    print(f"⚠️ Could not read W2 file: {w2_file.name} - {e}")

            if not matched_w2:
                print(f"⚠️ No matching W2 found for {first} {last} in {file.name}")
                continue

            try:
                writer = PdfWriter()

                # Remove first 2 pages of STFCS
                stfcs_reader = PdfReader(str(file))
                for page in stfcs_reader.pages[2:]:
                    writer.add_page(page)

                # Append first page of matched W2
                w2_reader = PdfReader(str(matched_w2))
                writer.add_page(w2_reader.pages[0])

                # Save final PDF
                output_filename = generate_random_filename(first, last)
                output_path = state_path / output_filename
                with open(output_path, 'wb') as f:
                    writer.write(f)

                print(f"✅ Processed: {output_filename}")

            except Exception as e:
                print(f"❌ Error processing {file.name} with W2 {matched_w2.name if matched_w2 else 'N/A'}: {e}")
