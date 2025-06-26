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
            company = self.work_dir / 'company'
            w2 = self.work_dir / 'W2'
            output_data = self.work_dir / 'output_data'
            federal = self.work_dir / 'federal'
            state = self.work_dir / 'state'
            combined = self.work_dir / 'combined'
            envelopes = self.work_dir / 'envelopes'

            people_dirs = list(output_data.glob('peopleinput*/docs'))

            process_federal_files(company, federal)
            attach_w2_to_stfcs(company, w2, state)
            # combine_state_files(state, combined)
            # create_envelope_docs(combined, people_dirs, envelopes)

            messagebox.showinfo("Done", "All processing complete!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = SortFilesApp(root)
    root.mainloop()
