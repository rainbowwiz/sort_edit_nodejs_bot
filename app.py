import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from processors.federal_processor import process_federal_files
from processors.state_processor import attach_w2_to_stfcs
from processors.combiner import combine_state_files
from processors.envelope_creator import create_envelope_docs

class SortFilesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sort Files Software")
        self.root.geometry("450x250")
        self.work_dir = None

        self.label = tk.Label(root, text="Please select your work directory", wraplength=400)
        self.label.pack(pady=10)

        self.select_btn = tk.Button(root, text="Select Work Directory", command=self.select_directory)
        self.select_btn.pack(pady=5)

        self.process_btn = tk.Button(root, text="Start Processing", command=self.run_workflow, state=tk.DISABLED)
        self.process_btn.pack(pady=15)

    def select_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.work_dir = Path(folder_selected)
            self.label.config(text=f"Selected: {self.work_dir}")
            self.process_btn.config(state=tk.NORMAL)

    def run_workflow(self):
        try:
            print(f"📁 Starting workflow with work directory: {self.work_dir}")
            company = self.work_dir / 'company'
            w2 = self.work_dir / 'W2'
            output_data = self.work_dir / 'output_data'
            federal = self.work_dir / 'federal'
            state = self.work_dir / 'state'
            combined = self.work_dir / 'combined'
            envelopes = self.work_dir / 'envelopes'

            people_dirs = list(output_data.glob('peopleinput*/docs'))
            print(f"📁 Found {len(people_dirs)} peopleinput*/docs directories")

            # Step 1: Process federal files (commented out until needed)
            print("📄 Running process_federal_files")
            # process_federal_files(company, federal)

            # Step 2: Attach W2 pages to STFCS files
            print("📄 Running attach_w2_to_stfcs")
            # attach_w2_to_stfcs(company, w2, state)

            # Step 3: Combine state files into groups of up to 30
            print("📄 Running combine_state_files")
            all_name_lists = combine_state_files(state, combined)
            print(f"✅ Retrieved name lists for {len(all_name_lists)} combined PDFs")
            for i, name_list in enumerate(all_name_lists, 1):
                print(f"Combined PDF {i} names: {name_list}")

            # Step 4: Create envelope documents (commented out until requirements provided)
            print("📄 Running create_envelope_docs")
            create_envelope_docs(combined, people_dirs, all_name_lists, envelopes)

            messagebox.showinfo("Done", "All processing complete!")
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = SortFilesApp(root)
    root.mainloop()