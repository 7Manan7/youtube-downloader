import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import os
from datetime import datetime


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced YouTube Downloader")
        self.root.geometry("800x600")

        # Variables
        self.url = tk.StringVar()
        self.output_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.status = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar(value=0)
        self.selected_resolution = tk.StringVar(value="1080p")
        self.selected_codec = tk.StringVar(value="h264")
        self.selected_audio_quality = tk.StringVar(value="192K")
        self.download_playlist = tk.BooleanVar(value=False)
        self.extract_audio_only = tk.BooleanVar(value=False)
        self.add_metadata = tk.BooleanVar(value=True)
        self.available_formats = []
        
        # UI Elements
        self.create_widgets()
        
        # Add theme
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=2)

    def get_unique_filename(self, directory, filename):
        """Add _1, _2, etc. if file exists"""
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename

        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{base}_{counter}{ext}"
            counter += 1

        return new_filename

    def create_widgets(self):
        # URL Entry
        ttk.Label(self.root, text="YouTube URL:").pack(pady=(10, 0), padx=10, anchor="w")
        url_frame = ttk.Frame(self.root)
        url_frame.pack(pady=(0, 10), padx=10, fill="x")

        url_entry = ttk.Entry(url_frame, textvariable=self.url, width=50)
        url_entry.pack(side="left", fill="x", expand=True)

        fetch_btn = ttk.Button(url_frame, text="Check Available", command=self.fetch_formats)
        fetch_btn.pack(side="right", padx=(5, 0))

        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="Download Options")
        options_frame.pack(pady=10, padx=10, fill="x")

        # Resolution and Codec Selection
        ttk.Label(options_frame, text="Video Resolution:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.resolution_combo = ttk.Combobox(options_frame, textvariable=self.selected_resolution,
                                           values=["4320p (8K)", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p"],
                                           state="readonly", width=15)
        self.resolution_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(options_frame, text="Video Codec:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.codec_combo = ttk.Combobox(options_frame, textvariable=self.selected_codec,
                                      values=["h264", "h265", "av1", "vp9", "best available"],
                                      state="readonly", width=15)
        self.codec_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Audio Quality Selection
        ttk.Label(options_frame, text="Audio Quality:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.audio_quality_combo = ttk.Combobox(options_frame, textvariable=self.selected_audio_quality,
                                              values=["320K", "256K", "192K", "128K", "96K", "64K"],
                                              state="readonly", width=15)
        self.audio_quality_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Additional Options
        options_subframe = ttk.Frame(options_frame)
        options_subframe.grid(row=2, column=0, columnspan=4, pady=5, sticky="w")

        ttk.Checkbutton(options_subframe, text="Download Playlist (if URL is playlist)",
                       variable=self.download_playlist).pack(side="left", padx=5)
        ttk.Checkbutton(options_subframe, text="Extract Audio Only (MP3)",
                       variable=self.extract_audio_only).pack(side="left", padx=5)
        ttk.Checkbutton(options_subframe, text="Add Metadata",
                       variable=self.add_metadata).pack(side="left", padx=5)

        # Output Path
        ttk.Label(self.root, text="Save Location:").pack(pady=(10, 0), padx=10, anchor="w")
        path_frame = ttk.Frame(self.root)
        path_frame.pack(pady=(0, 10), padx=10, fill="x")

        path_entry = ttk.Entry(path_frame, textvariable=self.output_path)
        path_entry.pack(side="left", fill="x", expand=True)

        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side="right", padx=(5, 0))

        # Download Button with modern style
        download_btn = ttk.Button(self.root, text="Download", command=self.start_download, style="Accent.TButton")
        download_btn.pack(pady=10)

        # Progress Frame
        progress_frame = ttk.LabelFrame(self.root, text="Download Progress")
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_value, maximum=100)
        self.progress.pack(fill="x", padx=10, pady=5)

        # Status Label
        self.status_label = ttk.Label(progress_frame, textvariable=self.status, wraplength=700)
        self.status_label.pack(pady=5, padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)

    def fetch_formats(self):
        url = self.url.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        Thread(target=self._fetch_formats_thread, daemon=True).start()

    def _fetch_formats_thread(self):
        url = self.url.get()
        self.status.set("Fetching available formats...")

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.root.after(0, self._update_status, f"Found: {info.get('title', 'video')}")

        except Exception as e:
            self.root.after(0, self._fetch_error, str(e))

    def _update_status(self, message):
        self.status.set(message)

    def _fetch_error(self, error):
        self.status.set(f"Error: {error}")
        messagebox.showerror("Error", f"Could not fetch video info:\n{error}")

    def start_download(self):
        if not self.url.get():
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        url = self.url.get()
        output_dir = self.output_path.get()
        resolution = self.selected_resolution.get().split()[0]
        codec = self.selected_codec.get()
        audio_quality = self.selected_audio_quality.get().replace("K", "")

        try:
            os.makedirs(output_dir, exist_ok=True)

            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '0%').strip('%')
                    try:
                        self.progress_value.set(float(percent))
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        self.status.set(f"Downloading... {d['_percent_str']} (Speed: {speed}, ETA: {eta})")
                    except:
                        pass
                elif d['status'] == 'finished':
                    self.progress_value.set(100)
                    self.status.set("Processing download...")

            # Format selection
            if self.extract_audio_only.get():
                format_str = "bestaudio/best"
                ext = "mp3"
            else:
                height = int(resolution.replace("p", ""))
                codec_filter = {
                    "h264": "[vcodec^=avc1]",
                    "h265": "[vcodec^=hev1]",
                    "av1": "[vcodec^=av01]",
                    "vp9": "[vcodec^=vp09]",
                    "best available": ""
                }[codec]
                format_str = f"bestvideo[height<={height}]{codec_filter}+bestaudio/best[height<={height}]"
                ext = "mp4"

            # Download options
            ydl_opts = {
                'format': format_str,
                'outtmpl': f'{output_dir}/%(title)s - %(resolution)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'noplaylist': not self.download_playlist.get(),
                'writethumbnail': self.add_metadata.get(),
                'writesubtitles': True,
                'writeautomaticsub': True,
            }

            if self.extract_audio_only.get():
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': audio_quality,
                    }],
                })
            else:
                ydl_opts['postprocessors'] = []
                if self.add_metadata.get():
                    ydl_opts['postprocessors'].extend([
                        {'key': 'FFmpegMetadata'},
                        {'key': 'EmbedThumbnail'},
                    ])

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if isinstance(info, dict):
                    title = info.get('title', 'video')
                    self.status.set(f"Successfully downloaded: {title}")
                else:
                    self.status.set("Download completed successfully!")

            messagebox.showinfo("Success", "Download completed successfully!")
            self.progress_value.set(0)

        except Exception as e:
            self.status.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            self.progress_value.set(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()