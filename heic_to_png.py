import os
from PIL import Image
import pillow_heif

# Enable HEIC support
pillow_heif.register_heif_opener()

# -------- CONFIG --------
INPUT_DIR = r"D:\MyMedia"   # CHANGE THIS
DELETE_ORIGINAL = False     # set True if you want to remove HEIC after conversion
# ------------------------


def convert_heic_to_png(filepath):
    try:
        with Image.open(filepath) as img:
            new_path = os.path.splitext(filepath)[0] + ".png"

            # Convert and save as PNG (lossless)
            img.convert("RGB").save(new_path, "PNG", compress_level=3)

            print(f"Converted: {filepath} -> {new_path}")

            if DELETE_ORIGINAL:
                os.remove(filepath)

    except Exception as e:
        print(f"Failed: {filepath} | Error: {e}")


def scan_and_convert():
    for root, dirs, files in os.walk(INPUT_DIR):
        for file in files:
            if file.lower().endswith(".heic"):
                full_path = os.path.join(root, file)
                convert_heic_to_png(full_path)


if __name__ == "__main__":
    scan_and_convert()
