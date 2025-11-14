import os
import sys
import logging
import ffmpeg
import colorlog
from dotenv import load_dotenv

# --- Konfiguracja ---
# Zmień tę wartość, aby dostosować kompresję.
# Niższa wartość = lepsza jakość, większy plik (np. 18-22).
# Wyższa wartość = gorsza jakość, mniejszy plik (np. 24-28).
# Wartość 23 jest uznawana za świetny kompromis.
COMPRESSION_CRF = int(os.getenv("COMPRESSION_CRF", "23"))
# --------------------


def setup_logging():
    """Konfiguruje kolorowe logowanie."""
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def compress_video(input_file, output_file):
    """
    Kompresuje pojedynczy plik wideo używając FFmpeg.
    Zachowuje oryginalną rozdzielczość (720p) i klatkaż (30fps),
    ale drastycznie zmniejsza rozmiar pliku przez rekompresję
    do kodeka H.264 (libx264) z audio AAC.
    """
    try:
        (
            ffmpeg.input(input_file)
            .output(
                output_file,
                vcodec="libx264",  # Użyj popularnego kodeka H.264
                crf=COMPRESSION_CRF,  # Ustaw stały współczynnik jakości
                preset="medium",  # Dobry balans między prędkością a kompresją
                acodec="aac",  # Użyj popularnego kodeka audio AAC
                audio_bitrate="128k",  # Standardowy bitrate dla audio
                pix_fmt="yuv420p",  # Zapewnia kompatybilność z odtwarzaczami
            )
            .overwrite_output()  # Nadpisz plik, jeśli już istnieje
            .run(quiet=True)  # Uruchom cicho (bez logów ffmpeg)
        )
        logging.info(f"Pomyślnie skompresowano: {os.path.basename(output_file)}")
    except ffmpeg.Error as e:
        logging.error(
            f"Błąd FFmpeg podczas przetwarzania {os.path.basename(input_file)}:"
        )
        # Dekodujemy błąd z stderr, aby pokazać komunikat z FFmpeg
        logging.error(e.stderr.decode("utf-8"))
    except Exception as e:
        logging.error(
            f"Nieoczekiwany błąd przy pliku {os.path.basename(input_file)}: {e}"
        )


def main():
    """Główna funkcja skryptu."""
    load_dotenv()

    input_dir = os.getenv("INPUT_PATH")
    output_dir = os.getenv("OUTPUT_PATH")

    # --- Walidacja ścieżek ---
    if not input_dir or not output_dir:
        logging.critical("Brak definicji INPUT_PATH lub OUTPUT_PATH w pliku .env!")
        sys.exit(1)

    if not os.path.isdir(input_dir):
        logging.critical(f"Ścieżka wejściowa nie istnieje: {input_dir}")
        sys.exit(1)

    try:
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Katalog wejściowy: {input_dir}")
        logging.info(f"Katalog wyjściowy: {output_dir}")
    except OSError as e:
        logging.critical(f"Nie można utworzyć katalogu wyjściowego {output_dir}: {e}")
        sys.exit(1)

    # --- Przetwarzanie plików ---
    logging.info("Rozpoczynanie przetwarzania plików MP4...")
    processed_count = 0

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".mp4"):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename)

            logging.info(f"Przetwarzanie pliku: {filename}")
            compress_video(input_file_path, output_file_path)
            processed_count += 1

    if processed_count == 0:
        logging.warning("Nie znaleziono żadnych plików .mp4 w katalogu wejściowym.")
    else:
        logging.info(f"Zakończono. Przetworzono łącznie {processed_count} plików.")


if __name__ == "__main__":
    setup_logging()
    main()
