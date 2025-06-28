import re
from datetime import datetime
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError

def combine_state_files(state_path: Path, combined_path: Path):
    """Combine up to 30 PDF files from state directory into combined PDFs, returning name lists."""
    # Create combined directory if it doesn't exist
    combined_path.mkdir(exist_ok=True)
    print(f"📁 Ensured combined directory exists: {combined_path}")

    # Track processed files and name lists for all combined PDFs
    processed_files = set()
    all_name_lists = []  # List of lists: [[(Last1, First1), ...], ...]

    while True:
        # Get all PDF files in state directory
        all_files = sorted(state_path.glob('*.pdf'))
        # Filter out already processed files
        unprocessed_files = [f for f in all_files if f.name not in processed_files]

        if not unprocessed_files:
            print("✅ No unprocessed files remain in state directory. Combining complete.")
            break

        # Extract 6-digit number from filenames and sort
        file_info = []
        for file in unprocessed_files:
            match = re.match(r'([A-Za-z\-]+)_([A-Za-z]+)_(\d{6})\.pdf$', file.name)
            if match:
                last, first, digits = match.groups()
                file_info.append((file, last, first, int(digits)))
            else:
                print(f"⚠️ Skipping {file.name}: Invalid filename format")
                processed_files.add(file.name)  # Skip to avoid infinite loop

        if not file_info:
            print("⚠️ No valid unprocessed files found. Combining complete.")
            break

        # Sort by 6-digit number and select up to 30 files
        file_info.sort(key=lambda x: x[3])  # Sort by digits
        selected_files = file_info[:30]  # Take up to 30
        print(f"📄 Selected {len(selected_files)} files for combining")

        # Track names in order
        name_list = [(last, first) for _, last, first, _ in selected_files]

        # Combine selected files into one PDF
        try:
            writer = PdfWriter()
            for file, _, _, _ in selected_files:
                try:
                    reader = PdfReader(str(file))
                    if len(reader.pages) < 1:
                        print(f"⚠️ Skipping {file.name}: No pages found")
                        continue
                    for page in reader.pages:
                        writer.add_page(page)
                    print(f"✅ Added {file.name} to combined PDF")
                    processed_files.add(file.name)
                except PdfReadError as e:
                    print(f"❌ Skipping {file.name}: PDF read error - {e}")
                    processed_files.add(file.name)
                except Exception as e:
                    print(f"❌ Skipping {file.name}: Unexpected error - {e}")
                    processed_files.add(file.name)

            # Save combined PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"combined_{timestamp}.pdf"
            output_path = combined_path / output_filename
            with open(output_path, 'wb') as f:
                writer.write(f)
            print(f"✅ Saved combined PDF: {output_filename} with {len(name_list)} files")

            # Append name list for this combined PDF
            all_name_lists.append(name_list)

        except Exception as e:
            print(f"❌ Error saving combined PDF: {e}")
            continue

    return all_name_lists