import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os

from transcriber import Transcriber
from subtitle_generator import SubtitleGenerator
from utils import overlay_subtitles

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Transcription App")

        self.video_path = tk.StringVar()

        tk.Label(root, text="Select Video File:").pack(pady=5)
        tk.Entry(root, textvariable=self.video_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(root, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(root, text="Start", command=self.start_transcription)
        self.start_btn.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        if file_path:
            self.video_path.set(file_path)

    def start_transcription(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file.")
            return
        self.start_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Processing...")
        threading.Thread(target=self.run_transcription).start()

    def run_transcription(self):
        try:
            self.progress["value"] = 0
            self.root.update_idletasks()

            # Step 1: Transcribe
            transcriber = Transcriber(self.video_path.get())
            transcriber.transcribe_audio()
            self.progress["value"] = 30
            self.root.update_idletasks()

            transcription = transcriber.get_transcription()

            # Step 2: Generate SRT
            srt_path = "subtitles.srt"
            subtitle_generator = SubtitleGenerator()
            subtitle_generator.generate_subtitles(transcription, srt_path)
            self.progress["value"] = 60
            self.root.update_idletasks()

            # Step 3: Overlay subtitles
            output_video_path = "output_with_subtitles.mp4"
            overlay_subtitles(self.video_path.get(), srt_path, output_video_path)
            self.progress["value"] = 100
            self.root.update_idletasks()

            self.status_label.config(text="Done! Output saved as output_with_subtitles.mp4")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
        finally:
            self.start_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()