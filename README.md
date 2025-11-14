# Skrypt do Kompresji Wideo

Prosty skrypt Pythona do wsadowej (batch) kompresji plików `.mp4`. Używa **FFmpeg** do rekompresji wideo do kodeka **H.264 (libx264)**, aby drastycznie zmniejszyć rozmiar plików przy zachowaniu dobrej jakości.

## 🛠️ Wymagania

* **Python 3.x**
* **FFmpeg**: Musi być zainstalowany w systemie i dodany do globalnej zmiennej środowiskowej `PATH`.
* **Biblioteki Python**:
    ```bash
    pip install ffmpeg-python colorlog python-dotenv
    ```

## ⚙️ Konfiguracja

Skrypt jest konfigurowany za pomocą pliku `.env`. Skopiuj `env.template` do nowego pliku o nazwie `.env` i dostosuj ścieżki oraz poziom kompresji.

**Zawartość `.env.template`:**

```ini
INPUT_PATH=E:\Videos\Input
OUTPUT_PATH=E:\Videos\Output
COMPRESSION_CRF=23
```
* `INPUT_PATH`: Folder ze źródłowymi plikami `.mp4`.
* `OUTPUT_PATH`: Folder, do którego zostaną zapisane skompresowane kopie.
* `COMPRESSION_CRF`: **Constant Rate Factor**. Kontroluje jakość i rozmiar pliku.
    * **Niższa wartość** = Lepsza jakość, większy plik (np. `18`).
    * **Wyższa wartość** = Gorsza jakość, mniejszy plik (np. `28`).
    * Wartość `23` jest uznawana za domyślny, dobry kompromis.

---

## 🚀 Uruchomienie

1.  Upewnij się, że wszystkie wymagania są spełnione, a plik `.env` jest poprawnie skonfigurowany.
2.  Umieść pliki wideo, które chcesz skompresować, w folderze `INPUT_PATH`.
3.  Uruchom skrypt:

    ```bash
    python main.py
    ```

4.  Skompresowane pliki pojawią się w folderze `OUTPUT_PATH`.