import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
from PIL import Image, ImageTk
import customtkinter as ctk

from transcriber import Transcriber
from subtitle_generator import SubtitleGenerator
from utils import overlay_subtitles

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernTranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 AI Video Transcription Studio")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Variables
        self.video_path = tk.StringVar()
        self.is_processing = False
        
        # Options variables
        self.show_options = tk.BooleanVar(value=False)
        self.word_mode = tk.BooleanVar(value=True)  # True for words, False for lines
        self.font_size = tk.IntVar(value=28)
        self.font_family = tk.StringVar(value="Bangers-Regular.ttf")
        self.font_color = tk.StringVar(value="white")
        self.highlight_color = tk.StringVar(value="yellow")
        self.bottom_padding = tk.IntVar(value=100)
        
        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        # Main container with padding
        main_frame = ctk.CTkFrame(self.root, corner_radius=20)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header section
        self.create_header(main_frame)
        
        # Content section
        self.create_content(main_frame)
        
        # Options section (initially hidden)
        self.create_options_section(main_frame)
        
        # Footer section
        self.create_footer(main_frame)

    def create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Top row with title and options button
        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            top_row, 
            text="🎬 AI Video Transcription Studio",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#1f538d", "#14375e")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Options button
        self.options_btn = ctk.CTkButton(
            top_row,
            text="⚙️ Options",
            command=self.toggle_options,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            height=35,
            corner_radius=10
        )
        self.options_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Transform your videos with AI-powered subtitles",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90")
        )
        subtitle_label.grid(row=1, column=0, sticky="ew", pady=(10, 0))

    def create_content(self, parent):
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # File selection section
        self.create_file_section(content_frame)
        
        # Processing section
        self.create_processing_section(content_frame)

    def create_file_section(self, parent):
        file_frame = ctk.CTkFrame(parent, corner_radius=15)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        file_frame.grid_columnconfigure(1, weight=1)
        
        # File selection label
        file_label = ctk.CTkLabel(
            file_frame,
            text="📁 Select Video File",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        file_label.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(20, 10))
        
        # File path entry
        self.file_entry = ctk.CTkEntry(
            file_frame,
            textvariable=self.video_path,
            placeholder_text="Choose a video file to transcribe...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.file_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(20, 10), pady=(0, 20))
        
        # Browse button
        self.browse_btn = ctk.CTkButton(
            file_frame,
            text="Browse",
            command=self.browse_file,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=100,
            corner_radius=10
        )
        self.browse_btn.grid(row=1, column=2, padx=(0, 20), pady=(0, 20))

    def create_processing_section(self, parent):
        process_frame = ctk.CTkFrame(parent, corner_radius=15)
        process_frame.grid(row=1, column=0, sticky="nsew")
        process_frame.grid_rowconfigure(1, weight=1)
        process_frame.grid_columnconfigure(0, weight=1)
        
        # Process button
        self.process_btn = ctk.CTkButton(
            process_frame,
            text="🚀 Start Transcription",
            command=self.start_transcription,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=15,
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#14375e", "#1f538d")
        )
        self.process_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Progress section
        progress_container = ctk.CTkFrame(process_frame, fg_color="transparent")
        progress_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        progress_container.grid_rowconfigure(1, weight=1)
        progress_container.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            height=20,
            corner_radius=10,
            fg_color=("gray80", "gray20"),
            progress_color=("#1f538d", "#14375e")
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            progress_container,
            text="Ready to transcribe your video",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90")
        )
        self.status_label.grid(row=1, column=0, sticky="ew")
        
        # Step indicators
        self.create_step_indicators(progress_container)

    def create_step_indicators(self, parent):
        steps_frame = ctk.CTkFrame(parent, fg_color="transparent")
        steps_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        steps_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.steps = [
            {"text": "🎵 Transcribing Audio", "var": tk.BooleanVar()},
            {"text": "📝 Generating Subtitles", "var": tk.BooleanVar()},
            {"text": "🎬 Overlaying Video", "var": tk.BooleanVar()}
        ]
        
        for i, step in enumerate(self.steps):
            step_frame = ctk.CTkFrame(steps_frame, corner_radius=10, fg_color=("gray90", "gray20"))
            step_frame.grid(row=0, column=i, sticky="ew", padx=5)
            
            step_label = ctk.CTkLabel(
                step_frame,
                text=step["text"],
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray70")
            )
            step_label.pack(pady=10)
            
            # Add checkbox indicator
            step["checkbox"] = ctk.CTkCheckBox(
                step_frame,
                text="",
                variable=step["var"],
                state="disabled",
                width=20,
                height=20
            )
            step["checkbox"].pack(pady=(0, 10))

    def create_footer(self, parent):
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 30))
        
        # Info text
        info_text = ctk.CTkLabel(
            footer_frame,
            text="💡 Tip: Supported formats include MP4, AVI, MOV, and more",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70")
        )
        info_text.pack()

    def create_options_section(self, parent):
        """Create the options panel with styling controls"""
        self.options_frame = ctk.CTkFrame(parent, corner_radius=15)
        self.options_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 20))
        self.options_frame.grid_columnconfigure(1, weight=1)
        
        # Initially hidden
        self.options_frame.grid_remove()
        
        # Options title
        options_title = ctk.CTkLabel(
            self.options_frame,
            text="🎨 Subtitle Styling Options",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        options_title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 15))
        
        # Word/Line mode toggle
        mode_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Display Mode:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        mode_label.pack(side="left")
        
        self.word_mode_checkbox = ctk.CTkCheckBox(
            mode_frame,
            text="Word-by-word (with highlighting)",
            variable=self.word_mode,
            font=ctk.CTkFont(size=12)
        )
        self.word_mode_checkbox.pack(side="left", padx=(20, 0))
        
        # Font settings
        font_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        font_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        font_frame.grid_columnconfigure(1, weight=1)
        
        # Font family
        font_family_label = ctk.CTkLabel(
            font_frame,
            text="Font Family:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        font_family_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.font_family_entry = ctk.CTkEntry(
            font_frame,
            textvariable=self.font_family,
            placeholder_text="Arial-Bold or /path/to/font.ttf",
            width=200
        )
        self.font_family_entry.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Font file browser button
        self.font_browse_btn = ctk.CTkButton(
            font_frame,
            text="📁 Browse",
            command=self.browse_font,
            font=ctk.CTkFont(size=10),
            width=80,
            height=25
        )
        self.font_browse_btn.grid(row=0, column=2, sticky="w", padx=(5, 0), pady=5)
        
        # Font size
        font_size_label = ctk.CTkLabel(
            font_frame,
            text="Font Size:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        font_size_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.font_size_slider = ctk.CTkSlider(
            font_frame,
            from_=16,
            to=48,
            variable=self.font_size,
            width=200
        )
        self.font_size_slider.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        self.font_size_value = ctk.CTkLabel(
            font_frame,
            textvariable=self.font_size,
            font=ctk.CTkFont(size=12)
        )
        self.font_size_value.grid(row=1, column=2, sticky="w", padx=(10, 0), pady=5)
        
        # Colors
        color_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        color_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        color_frame.grid_columnconfigure(1, weight=1)
        
        # Font color
        font_color_label = ctk.CTkLabel(
            color_frame,
            text="Font Color:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        font_color_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.font_color_entry = ctk.CTkEntry(
            color_frame,
            textvariable=self.font_color,
            placeholder_text="white",
            width=150
        )
        self.font_color_entry.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Highlight color
        highlight_color_label = ctk.CTkLabel(
            color_frame,
            text="Highlight Color:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        highlight_color_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.highlight_color_entry = ctk.CTkEntry(
            color_frame,
            textvariable=self.highlight_color,
            placeholder_text="yellow",
            width=150
        )
        self.highlight_color_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Bottom padding
        padding_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        padding_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        padding_frame.grid_columnconfigure(1, weight=1)
        
        padding_label = ctk.CTkLabel(
            padding_frame,
            text="Bottom Padding:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        padding_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.padding_slider = ctk.CTkSlider(
            padding_frame,
            from_=50,
            to=200,
            variable=self.bottom_padding,
            width=200
        )
        self.padding_slider.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        self.padding_value = ctk.CTkLabel(
            padding_frame,
            textvariable=self.bottom_padding,
            font=ctk.CTkFont(size=12)
        )
        self.padding_value.grid(row=0, column=2, sticky="w", padx=(10, 0), pady=5)
        
        # Apply button
        apply_btn = ctk.CTkButton(
            self.options_frame,
            text="✅ Apply Settings",
            command=self.apply_settings,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10
        )
        apply_btn.grid(row=5, column=0, columnspan=2, pady=20)

    def toggle_options(self):
        """Toggle the options panel visibility"""
        if self.show_options.get():
            self.options_frame.grid_remove()
            self.options_btn.configure(text="⚙️ Options")
            self.show_options.set(False)
        else:
            self.options_frame.grid()
            self.options_btn.configure(text="❌ Close Options")
            self.show_options.set(True)

    def browse_font(self):
        """Browse for font file"""
        font_path = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=[
                ("Font files", "*.ttf *.otf *.woff *.woff2"),
                ("TrueType fonts", "*.ttf"),
                ("OpenType fonts", "*.otf"),
                ("All files", "*.*")
            ]
        )
        if font_path:
            self.font_family.set(font_path)

    def apply_settings(self):
        """Apply the current settings"""
        # Update the button text to show settings were applied
        self.options_btn.configure(text="✅ Applied")
        self.root.after(2000, lambda: self.options_btn.configure(text="⚙️ Options"))

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("MP4 files", "*.mp4"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.video_path.set(file_path)
            self.status_label.configure(text=f"Selected: {os.path.basename(file_path)}")

    def start_transcription(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file first.")
            return
        
        if self.is_processing:
            return
            
        self.is_processing = True
        self.process_btn.configure(state="disabled", text="⏳ Processing...")
        self.status_label.configure(text="Starting transcription process...")
        
        # Reset step indicators
        for step in self.steps:
            step["var"].set(False)
            step["checkbox"].configure(state="normal")
        
        # Start processing in separate thread
        threading.Thread(target=self.run_transcription, daemon=True).start()

    def run_transcription(self):
        try:
            # Step 1: Transcribe Audio
            self.update_progress(0, "🎵 Extracting and transcribing audio...")
            self.steps[0]["var"].set(True)

            transcriber = Transcriber(self.video_path.get())
            transcriber.transcribe_audio()
            transcription = transcriber.get_transcription()

            # Step 2: Generate Subtitles
            self.update_progress(30, "📝 Generating subtitle file...")
            self.steps[1]["var"].set(True)
            
            srt_path = "subtitles.srt"
            subtitle_generator = SubtitleGenerator()
            # Pass word mode setting to subtitle generator
            subtitle_generator.generate_subtitles(transcription, srt_path, word_mode=self.word_mode.get())
            
            # Step 3: Overlay Subtitles
            self.update_progress(60, "🎬 Creating video with subtitles...")
            self.steps[2]["var"].set(True)
            
            output_video_path = "output_with_subtitles.mp4"
            # Use settings from options panel
            overlay_subtitles(
                self.video_path.get(), 
                srt_path, 
                output_video_path,
                font_size=self.font_size.get(),
                font=self.font_family.get(),
                color=self.font_color.get(),
                bottom_padding=self.bottom_padding.get(),
                highlight_color=self.highlight_color.get()
            )
            
            # Complete
            self.update_progress(100, "✅ Transcription completed successfully!")
            self.status_label.configure(text=f"✅ Done! Output saved as {output_video_path}")
            
            # Show success message
            messagebox.showinfo(
                "Success!", 
                f"Transcription completed!\n\n"
                f"📁 Subtitle file: {srt_path}\n"
                f"🎬 Video with subtitles: {output_video_path}"
            )
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")
        finally:
            self.is_processing = False
            self.process_btn.configure(state="normal", text="🚀 Start Transcription")
            self.progress_bar.set(0)

    def update_progress(self, value, message):
        self.progress_bar.set(value / 100)
        self.status_label.configure(text=message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = ctk.CTk()
    app = ModernTranscriptionApp(root)
    root.mainloop()