import os
import threading
import subprocess
from datetime import datetime
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from downloader import ScribdDownloaderLogic 

class ModernScribdBatchDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Scribd Downloader Pro")
        self.root.geometry("950x700")
        self.root.minsize(850, 600)
        
        self.colors = {
            "bg": "#090C11",             
            "panel": "#262B32",          
            "dark": "#090C11",           
            "accent": "#FFD300",         
            "accent_hover": "#E6BE00",   
            "secondary": "#757B81",      
            "secondary_hover": "#8C9298",
            "text_main": "#FFFFFF",      
            "text_muted": "#757B81",     
            "text_on_accent": "#090C11", 
            "danger": "#D9534F",         
            "danger_hover": "#C9302C"
        }
        
        self.root.configure(bg=self.colors["bg"])
        
        self.font_h1 = ("Segoe UI", 22, "bold")
        self.font_h2 = ("Segoe UI", 14, "bold")
        self.font_normal = ("Segoe UI", 10)
        self.font_small = ("Segoe UI", 9)

        self.image_refs = []

        self.logic = ScribdDownloaderLogic(
            log_cb=self.append_log,
            progress_cb=self.update_progress,
            status_cb=self.update_status,
            finish_cb=self.on_download_finish
        )

        self.setup_ui()
        self.load_existing_history()

    def create_hover_button(self, parent, text, bg, hover_bg, fg, command, **kwargs):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), width=12, 
                        bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
                        relief=tk.FLAT, bd=0, cursor="hand2", command=command, **kwargs)
        btn.bind("<Enter>", lambda e: e.widget.config(bg=hover_bg) if e.widget['state'] != tk.DISABLED else None)
        btn.bind("<Leave>", lambda e: e.widget.config(bg=bg) if e.widget['state'] != tk.DISABLED else None)
        return btn

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        left_panel = tk.Frame(main_frame, bg=self.colors["panel"], padx=25, pady=25)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=(0, 20))
        
        tk.Label(left_panel, text="ID Dokumen", font=self.font_h2, bg=self.colors["panel"], fg=self.colors["text_main"]).pack(anchor="w")
        tk.Label(left_panel, text="Pisahkan ID dengan baris baru", font=self.font_small, bg=self.colors["panel"], fg=self.colors["text_muted"]).pack(anchor="w", pady=(0, 15))
        
        input_container = tk.Frame(left_panel, bg=self.colors["dark"], padx=10, pady=10)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        self.id_input = tk.Text(input_container, width=22, height=8, font=self.font_normal, 
                                bg=self.colors["dark"], fg=self.colors["text_main"], 
                                insertbackground=self.colors["text_main"], bd=0, highlightthickness=0)
        self.id_input.pack(fill=tk.BOTH, expand=True)

        mid_panel = tk.Frame(main_frame, bg=self.colors["bg"])
        mid_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=(0, 20))
        
        self.lbl_title = tk.Label(mid_panel, text="Menunggu Dokumen...", font=self.font_h1, bg=self.colors["bg"], fg=self.colors["text_main"])
        self.lbl_title.pack(anchor="w", pady=(0, 10))
        
        self.canvas_prog = tk.Canvas(mid_panel, height=6, bg=self.colors["panel"], bd=0, highlightthickness=0)
        self.canvas_prog.pack(fill=tk.X, pady=(5, 10))
        self.prog_rect = self.canvas_prog.create_rectangle(0, 0, 0, 6, fill=self.colors["accent"], outline="")

        prog_text_frame = tk.Frame(mid_panel, bg=self.colors["bg"])
        prog_text_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.lbl_prog_left = tk.Label(prog_text_frame, text="0 / 0 Halaman", font=self.font_normal, bg=self.colors["bg"], fg=self.colors["text_muted"])
        self.lbl_prog_left.pack(side=tk.LEFT)
        
        self.lbl_prog_right = tk.Label(prog_text_frame, text="Ready", font=self.font_normal, bg=self.colors["bg"], fg=self.colors["accent"])
        self.lbl_prog_right.pack(side=tk.RIGHT)

        self.meta_panel = tk.Frame(mid_panel, bg=self.colors["panel"], pady=25, padx=20)
        self.meta_panel.pack(fill=tk.BOTH, expand=True)
        self.lbl_metadata = tk.Label(self.meta_panel, text="Sistem Siap.\n\nFile akan tersimpan di:\nScribd_Downloads", 
                                     font=self.font_normal, bg=self.colors["panel"], fg=self.colors["text_main"], justify=tk.CENTER)
        self.lbl_metadata.pack(expand=True)

        right_panel = tk.Frame(main_frame, bg=self.colors["bg"])
        right_panel.grid(row=0, column=2, sticky="n", pady=(0, 20))
        
        self.btn_start = self.create_hover_button(
            right_panel, text="Start", 
            bg=self.colors["accent"], hover_bg=self.colors["accent_hover"], 
            fg=self.colors["text_on_accent"], command=self.start_batch
        )
        self.btn_start.pack(pady=(0, 15), ipady=8)
        
        self.btn_cancel = self.create_hover_button(
            right_panel, text="Cancel", 
            bg=self.colors["panel"], hover_bg=self.colors["panel"], 
            fg=self.colors["text_muted"], command=self.cancel_batch, state=tk.DISABLED
        )
        self.btn_cancel.pack(ipady=8)

        history_outer = tk.Frame(main_frame, bg=self.colors["dark"], padx=5, pady=5)
        history_outer.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.history_canvas = tk.Canvas(history_outer, bg=self.colors["dark"], bd=0, highlightthickness=0)
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(history_outer, orient="vertical", command=self.history_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.history_inner_frame = tk.Frame(self.history_canvas, bg=self.colors["dark"], padx=15, pady=15)
        self.history_window = self.history_canvas.create_window((0, 0), window=self.history_inner_frame, anchor="nw")
        
        self.history_inner_frame.bind("<Configure>", lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all")))
        self.history_canvas.bind("<Configure>", lambda e: self.history_canvas.itemconfig(self.history_window, width=e.width))

    def start_batch(self):
        raw_text = self.id_input.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showerror("Error", "Harap masukkan setidaknya satu ID Dokumen!")
            return
            
        doc_ids = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        self.btn_start.config(state=tk.DISABLED, bg=self.colors["panel"], fg=self.colors["text_muted"])
        self.btn_cancel.config(state=tk.NORMAL, bg=self.colors["danger"], fg=self.colors["text_main"])
        self.btn_cancel.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["danger_hover"]))
        self.btn_cancel.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["danger"]))
        
        self.lbl_title.config(text="Memulai Proses...")
        self.lbl_metadata.config(text=f"Mempersiapkan {len(doc_ids)} dokumen...\nHarap tunggu.")
        self.update_progress(0, 100)
        
        threading.Thread(target=self.logic.process_batch, args=(doc_ids,), daemon=True).start()

    def cancel_batch(self):
        self.btn_cancel.config(state=tk.DISABLED, text="Canceling...")
        self.logic.cancel_download()

    def on_download_finish(self):
        def reset_buttons():
            self.btn_start.config(state=tk.NORMAL, bg=self.colors["accent"], fg=self.colors["text_on_accent"])
            self.btn_cancel.config(state=tk.DISABLED, bg=self.colors["panel"], fg=self.colors["text_muted"], text="Cancel")
            self.btn_cancel.bind("<Enter>", lambda e: None)
            self.btn_cancel.bind("<Leave>", lambda e: None)
            self.lbl_metadata.config(text="Proses Selesai / Berhenti.\nSilakan masukkan ID baru.")
        self.root.after(0, reset_buttons)

    def append_log(self, message, color_type=None):
        self.root.after(0, self._safe_append_log, message)

    def _safe_append_log(self, message):
        if "[*] Judul:" in message:
            title = message.split("[*] Judul: ")[-1]
            if len(title) > 40: title = title[:37] + "..."
            self.lbl_title.config(text=title)
            
        elif "[SUKSES] Tersimpan:" in message:
            filepath = message.split("Tersimpan: ")[-1].strip()
            self.add_history_item(filepath, at_top=True)
            
        elif "===" in message:
            pass
        else:
            clean_msg = message.replace("[*]", "").replace("[!]", "").replace("[ERROR]", "ERROR:").strip()
            self.lbl_metadata.config(text=f"Current Action:\n\n{clean_msg}")

    def update_progress(self, current, maximum):
        self.root.after(0, self._safe_update_progress, current, maximum)

    def _safe_update_progress(self, current, maximum):
        canvas_width = self.canvas_prog.winfo_width()
        fill_width = (current / maximum) * canvas_width if maximum > 0 else 0
        self.canvas_prog.coords(self.prog_rect, 0, 0, fill_width, 6)
        self.lbl_prog_left.config(text=f"{current} / {maximum} Halaman Diunduh")

    def update_status(self, text):
        self.root.after(0, lambda: self.lbl_prog_right.config(text=text.replace("Status: ", "")))
    
    def get_relative_time(self, timestamp):
        """Mengubah timestamp menjadi teks yang ramah dibaca (e.g., 'Kemarin')"""
        now = datetime.now()
        file_time = datetime.fromtimestamp(timestamp)
        
        date_diff = (now.date() - file_time.date()).days
        time_diff = (now - file_time).total_seconds()
        
        if date_diff == 0:
            if time_diff < 60: return "Baru saja"
            elif time_diff < 3600: return f"{int(time_diff // 60)} menit yang lalu"
            else: return f"{int(time_diff // 3600)} jam yang lalu"
        elif date_diff == 1:
            return "Kemarin"
        else:
            return f"{date_diff} hari yang lalu"

    def load_existing_history(self):
        """Memuat PDF dari sesi sebelumnya saat aplikasi dibuka"""
        if not os.path.exists(self.logic.download_dir):
            return
            
        files = []
        for f in os.listdir(self.logic.download_dir):
            if f.endswith('.pdf'):
                full_path = os.path.join(self.logic.download_dir, f)
                files.append((full_path, os.path.getmtime(full_path)))
                
        files.sort(key=lambda x: x[1], reverse=True)
        
        for filepath, mtime in files:
            self.add_history_item(filepath, timestamp=mtime, at_top=False)

    def add_history_item(self, filepath, timestamp=None, at_top=False):
        filename = os.path.basename(filepath)
        
        if timestamp is None: timestamp = time.time()
        time_str = self.get_relative_time(timestamp)
        
        existing_children = self.history_inner_frame.winfo_children()
        
        item_frame = tk.Frame(self.history_inner_frame, bg=self.colors["dark"])
        
        if at_top and existing_children:
            item_frame.pack(fill=tk.X, pady=(0, 15), before=existing_children[0])
        else:
            item_frame.pack(fill=tk.X, pady=(0, 15))
        
        thumb_canvas = tk.Canvas(item_frame, bg=self.colors["secondary"], width=45, height=60, bd=0, highlightthickness=0)
        thumb_canvas.pack(side=tk.LEFT, padx=(0, 15))
        
        def render_thumbnail():
            thumb_path = os.path.join(self.logic.thumb_dir, filename.replace('.pdf', '_thumb.jpg'))
            if os.path.exists(thumb_path):
                try:
                    img = Image.open(thumb_path)
                    img = img.resize((45, 60), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    thumb_canvas.create_image(22, 30, image=photo, anchor=tk.CENTER)
                    self.image_refs.append(photo) 
                except Exception:
                    pass 

        self.root.after(200, render_thumbnail)
        
        info_frame = tk.Frame(item_frame, bg=self.colors["dark"])
        info_frame.pack(side=tk.LEFT, fill=tk.Y, pady=2)
        
        tk.Label(info_frame, text=filename, font=("Segoe UI", 11, "bold"), bg=self.colors["dark"], fg=self.colors["text_main"]).pack(anchor="w")
        tk.Label(info_frame, text="Download Complete", font=self.font_small, bg=self.colors["dark"], fg=self.colors["accent"]).pack(anchor="w")
        
        link = tk.Label(info_frame, text="Show in Folder", font=("Segoe UI", 9, "underline"), bg=self.colors["dark"], fg=self.colors["text_muted"], cursor="hand2")
        link.pack(anchor="w", pady=(2, 0))
        
        link.bind("<Button-1>", lambda e, path=filepath: self.open_in_explorer(path))
        link.bind("<Enter>", lambda e: link.config(fg=self.colors["text_main"]))
        link.bind("<Leave>", lambda e: link.config(fg=self.colors["text_muted"]))
        
        tk.Label(item_frame, text=time_str, font=self.font_normal, bg=self.colors["dark"], fg=self.colors["text_muted"]).pack(side=tk.RIGHT, anchor="n")
        
        tk.Frame(item_frame, bg=self.colors["panel"], height=1).pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))

    def open_in_explorer(self, filepath):
        try:
            filepath = os.path.normpath(filepath)
            subprocess.Popen(rf'explorer /select,"{filepath}"')
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka folder:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernScribdBatchDownloaderUI(root)
    root.mainloop()