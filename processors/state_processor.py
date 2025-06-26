import re
import random
import string
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def extract_name_from_second_page(pdf_path: Path):
    """Extract full name from the second page of an STFCS file."""
    try:
        reader = PdfReader(str(pdf_path))
        if len(reader.pages) < 2:
            print(f"⚠️ PDF {pdf_path.name} has fewer than 2 pages")
            return None
        text = reader.pages[1].extract_text() or ""
        if not text.strip():
            print(f"⚠️ No text extracted from second page of {pdf_path.name}")
            return None
        # More robust regex for names (handles hyphens, apostrophes, spaces)
        match = re.search(
            r'for:\s+([A-Z][A-Za-z\'-]+)\s+([A-Z][A-Za-z\'-]+)',
            text,
            re.IGNORECASE
        )
        if match:
            return match.group(1).strip(), match.group(2).strip()
        print(f"⚠️ No name found in {pdf_path.name}")
        return None
    except Exception as e:
        print(f"❌ Error reading {pdf_path.name}: {e}")
        raise RuntimeError(f"Failed to read {pdf_path.name}: {e}")

def generate_random_filename(first: str, last: str) -> str:
    """Generate a random 6-digit filename based on the name."""
    rand_digits = ''.join(random.choices(string.digits, k=6))
    return f"{last}_{first}_{rand_digits}.pdf"

def attach_w2_to_stfcs(company_path: Path, w2_path: Path, state_path: Path):
    """Attach W2 page to STFCS file after stripping first 2 pages."""
    state_path.mkdir(exist_ok=True)
    print("Starting state processing")

    for subfolder in sorted(company_path.iterdir()):
        if not subfolder.is_dir():
            continue
        print(f"Processing subfolder: {subfolder.name}")

        for file in sorted(subfolder.glob('STFCS*.pdf')):
            try:
                # Extract name from second page
                name = extract_name_from_second_page(file)
                if not name:
                    print(f"Skipping {file.name}: Could not extract name")
                    continue

                first, last = name
                first_lower = first.lower()
                last_lower = last.lower()
                print(f"Processing {file.name} for {first} {last}")

                # Get the first W2 file in alphabetical order
                w2_files = sorted(w2_path.glob('*.pdf'))
                if not w2_files:
                    print(f"⚠️ No W2 files found for {first} {last}")
                    continue
                w2_file = w2_files[0]  # First file in alphabetical order
                matched_w2 = None

                # Search first W2 file for name
                try:
                    reader = PdfReader(str(w2_file))
                    for page in reader.pages:
                        text = (page.extract_text() or "").lower()
                        if first_lower in text and last_lower in text:
                            matched_w2 = w2_file
                            break
                except Exception as e:
                    print(f"❌ Could not read W2 file {w2_file.name}: {e}")
                    continue

                if not matched_w2:
                    print(f"⚠️ No matching W2 found for {first} {last} in {w2_file.name}")
                    continue

                # Process STFCS and W2 files
                try:
                    writer = PdfWriter()
                    stfcs_reader = PdfReader(str(file))
                    if len(stfcs_reader.pages) < 2:
                        print(f"⚠️ Skipping {file.name}: Fewer than 2 pages")
                        continue

                    # Add pages from STFCS (skip first 2)
                    for page in stfcs_reader.pages[2:]:
                        writer.add_page(page)

                    # Append first page of W2
                    w2_reader = PdfReader(str(matched_w2))
                    if w2_reader.pages:
                        writer.add_page(w2_reader.pages[0])

                    # Save output
                    output_filename = generate_random_filename(first, last)
                    output_path = state_path / output_filename
                    with open(output_path, 'wb') as f:
                        writer.write(f)
                    print(f"✅ Processed: {output_filename}")

                except Exception as e:
                    print(f"❌ Error processing {file.name} with W2 {matched_w2.name}: {e}")
                    raise RuntimeError(f"Failed to process {file.name}: {e}")

            except Exception as e:
                print(f"❌ Error in {file.name}: {e}")
                raise  # Propagate to GUI

    print("State processing complete")