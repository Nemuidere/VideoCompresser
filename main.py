import os
import sys
import threading
import shutil
import subprocess  # Potrzebne do ukrycia konsoli
import customtkinter as ctk  # Nowoczesne GUI
from tkinter import filedialog, messagebox
import ffmpeg

# --- Konfiguracja Wyglądu ---
ctk.set_appearance_mode("Dark")  # Tryb: "System" (domyślny), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Motyw kolorystyczny

class VideoCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Główne okno
        self.title("Video Compressor Pro 🚀")
        self.geometry("700x650")
        self.resizable(False, False)

        # Zmienne
        self.ffmpeg_path = ctk.StringVar()
        self.input_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        self.crf_value = ctk.IntVar(value=23)
        self.is_running = False

        # Auto-detekcja ffmpeg
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            self.ffmpeg_path.set(system_ffmpeg)

        self.create_widgets()

    def create_widgets(self):
        # --- Kontener Główny ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tytuł
        ctk.CTkLabel(self.main_frame, text="KOMPRESOR WIDEO", 
                     font=("Roboto Medium", 20)).pack(pady=(20, 10))

        # --- Sekcja Ścieżek ---
        self.create_path_entry("Ścieżka FFmpeg:", self.ffmpeg_path, self.select_ffmpeg)
        self.create_path_entry("Folder Źródłowy:", self.input_path, self.select_input)
        self.create_path_entry("Folder Docelowy:", self.output_path, self.select_output)

        # Separator
        ctk.CTkFrame(self.main_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=15)

        # --- Sekcja Jakości ---
        quality_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        quality_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(quality_frame, text="Jakość Kompresji (CRF)", font=("Roboto", 14)).pack(anchor="w")
        
        # Suwak i Etykieta
        slider_box = ctk.CTkFrame(quality_frame, fg_color="transparent")
        slider_box.pack(fill="x", pady=5)

        self.lbl_crf_val = ctk.CTkLabel(slider_box, text="23", font=("Roboto", 24, "bold"), text_color="#3B8ED0")
        self.lbl_crf_val.pack(side="right", padx=10)

        self.slider = ctk.CTkSlider(slider_box, from_=18, to=35, number_of_steps=17, 
                                    variable=self.crf_value, command=self.update_crf_label)
        self.slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(quality_frame, text="⬅ Lepsza Jakość (duży plik)  |  Mniejszy Rozmiar (gorsza jakość) ➡", 
                     text_color="gray60", font=("Roboto", 10)).pack()

        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(20, 5))
        self.progress_bar.set(0)
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Gotowy do akcji", text_color="gray70")
        self.lbl_status.pack(pady=(0, 10))

        # --- Przycisk Start ---
        self.btn_start = ctk.CTkButton(self.main_frame, text="ROZPOCZNIJ KOMPRESJĘ", 
                                       font=("Roboto", 14, "bold"), height=45,
                                       fg_color="#2CC985", hover_color="#25A66E",
                                       command=self.start_thread)
        self.btn_start.pack(fill="x", padx=20, pady=10)

        # --- Konsola Logów ---
        self.log_area = ctk.CTkTextbox(self.main_frame, height=150, font=("Consolas", 11))
        self.log_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_area.configure(state="disabled")

    def create_path_entry(self, label_text, variable, cmd):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(frame, text=label_text, width=110, anchor="w").pack(side="left")
        ctk.CTkEntry(frame, textvariable=variable).pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkButton(frame, text="📂", width=40, command=cmd).pack(side="right")

    # --- Funkcje Logiki ---
    def select_ffmpeg(self):
        path = filedialog.askopenfilename(filetypes=[("Pliki wykonywalne", "*.exe")])
        if path: self.ffmpeg_path.set(path)

    def select_input(self):
        path = filedialog.askdirectory()
        if path: self.input_path.set(path)

    def select_output(self):
        path = filedialog.askdirectory()
        if path: self.output_path.set(path)

    def update_crf_label(self, val):
        self.lbl_crf_val.configure(text=str(int(val)))

    def log(self, message, level="INFO"):
        self.log_area.configure(state="normal")
        color = "white"
        prefix = "ℹ️"
        if level == "SUCCESS": 
            prefix, color = "✅", "#2CC985" # Zielony
        elif level == "ERROR": 
            prefix, color = "❌", "#FF4D4D" # Czerwony
        
        # CustomTkinter Textbox nie wspiera kolorowania per linia tak łatwo jak tk, 
        # więc po prostu wrzucamy tekst.
        self.log_area.insert("end", f"{prefix} {message}\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def start_thread(self):
        if not all([self.input_path.get(), self.output_path.get(), self.ffmpeg_path.get()]):
            messagebox.showwarning("Braki", "Uzupełnij wszystkie ścieżki!")
            return
        
        if self.is_running: return

        self.is_running = True
        self.btn_start.configure(state="disabled", text="PRZETWARZANIE...", fg_color="gray")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.run_compression, daemon=True).start()

    def run_compression(self):
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        crf = int(self.crf_value.get())
        ffmpeg_exe = self.ffmpeg_path.get()

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        files = [f for f in os.listdir(input_dir) if f.lower().endswith('.mp4')]
        total = len(files)
        
        if total == 0:
            self.log("Brak plików .mp4!", "ERROR")
            self.reset_ui()
            return

        self.log(f"Start: {total} plików.", "INFO")
        
        # --- USTAWIENIA UKRYWANIA OKNA ---
        startup_info = None
        creation_flags = 0
        if os.name == 'nt':
            creation_flags = 0x08000000  # subprocess.CREATE_NO_WINDOW (Dla Windows)
        # ---------------------------------

        for i, filename in enumerate(files):
            in_f = os.path.join(input_dir, filename)
            out_f = os.path.join(output_dir, filename)
            
            self.lbl_status.configure(text=f"Przetwarzanie: {filename} ({i+1}/{total})")
            
            try:
                # KROK 1: Budujemy strukturę, ale NIE uruchamiamy jej przez bibliotekę
                stream = (
                    ffmpeg.input(in_f)
                    .output(out_f, vcodec="libx264", crf=crf, preset="medium", acodec="aac", audio_bitrate="128k")
                )
                
                # KROK 2: "Kompilujemy" polecenie do listy tekstowej (np. ['ffmpeg.exe', '-i', ...])
                cmd_args = stream.compile(cmd=ffmpeg_exe, overwrite_output=True)

                # KROK 3: Uruchamiamy ręcznie przez subprocess, gdzie 'creationflags' działa idealnie
                subprocess.run(
                    cmd_args, 
                    check=True,            # Rzuci błąd jeśli ffmpeg zwróci kod błędu
                    creationflags=creation_flags, # To ukrywa czarne okno
                    stdin=subprocess.DEVNULL,     # Odcina wejście (zapobiega błedom)
                    stdout=subprocess.DEVNULL,    # Wycisza wyjście standardowe
                    stderr=subprocess.PIPE        # Przechwytuje błędy (opcjonalnie)
                )

                self.log(f"Gotowe: {filename}", "SUCCESS")
            
            except subprocess.CalledProcessError as e:
                # Wyłapujemy błąd z subprocess (gdy ffmpeg zwróci błąd)
                self.log(f"Błąd FFmpeg przy pliku: {filename}", "ERROR")
            except ffmpeg.Error as e:
                self.log(f"Błąd konfiguracji FFmpeg: {filename}", "ERROR")
            except Exception as e:
                self.log(f"Nieoczekiwany błąd: {str(e)}", "ERROR")

            self.progress_bar.set((i + 1) / total)

        messagebox.showinfo("Sukces", "Zakończono!")
        self.reset_ui()

    def reset_ui(self):
        self.is_running = False
        self.btn_start.configure(state="normal", text="ROZPOCZNIJ KOMPRESJĘ", fg_color="#2CC985")
        self.lbl_status.configure(text="Gotowy do pracy")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = VideoCompressorApp()
    app.mainloop()