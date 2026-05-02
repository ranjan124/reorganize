import os
import shutil
import re
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import pillow_heif

# Enable HEIC support
pillow_heif.register_heif_opener()

# -------- CONFIG --------
ROOT_DIR = r"F:\toupload"  # CHANGE THIS
OUTPUT_DIR = os.path.join(ROOT_DIR, "organized")
DRY_RUN = False  # Set False to actually move/convert

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".heic"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv"}
# ------------------------


def get_exif_date(filepath):
    try:
        image = Image.open(filepath)
        exif = image._getexif()
        if not exif:
            return None

        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            if decoded in ["DateTimeOriginal", "DateTime"]:
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except:
        return None
    return None


def get_file_date(filepath):
    filename = os.path.basename(filepath)

    # 1. Filename date (YYYYMMDD)
    match = re.search(r"(20\d{2})(\d{2})(\d{2})", filename)
    if match:
        try:
            y, m, d = match.groups()
            return datetime(int(y), int(m), int(d))
        except:
            pass

    # 2. EXIF (images)
    if filepath.lower().endswith(tuple(IMAGE_EXT)):
        exif_date = get_exif_date(filepath)
        if exif_date:
            return exif_date

    stat = os.stat(filepath)

    # 3. Creation time
    try:
        return datetime.fromtimestamp(stat.st_ctime)
    except:
        pass

    # 4. Modified time
    try:
        return datetime.fromtimestamp(stat.st_mtime)
    except:
        return None


def get_media_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in IMAGE_EXT:
        return "images"
    elif ext in VIDEO_EXT:
        return "videos"
    return None


def get_target_folder(date_obj):
    if not date_obj:
        return os.path.join(OUTPUT_DIR, "unknown")
    return os.path.join(OUTPUT_DIR, date_obj.strftime("%d.%m.%Y"))


def move_file(filepath):
    media_type = get_media_type(filepath)
    if not media_type:
        return

    date_obj = get_file_date(filepath)
    target_base = get_target_folder(date_obj)
    target_dir = os.path.join(target_base, media_type)

    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    is_heic = ext.lower() == ".heic"

    # Target path
    if is_heic:
        target_path = os.path.join(target_dir, name + ".png")
    else:
        target_path = os.path.join(target_dir, filename)

    # Handle duplicates
    counter = 1
    while os.path.exists(target_path):
        if is_heic:
            target_path = os.path.join(target_dir, f"{name}_{counter}.png")
        else:
            target_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
        counter += 1

    if DRY_RUN:
        print(f"[DRY RUN] {filepath} -> {target_path}")
        return

    # Create folder only when needed
    os.makedirs(target_dir, exist_ok=True)

    if is_heic:
        try:
            with Image.open(filepath) as img:
                img.convert("RGB").save(target_path, "PNG", compress_level=3)
            os.remove(filepath)
            print(f"Converted + Moved: {filepath} -> {target_path}")
        except Exception as e:
            print(f"Failed HEIC: {filepath} | {e}")
    else:
        shutil.move(filepath, target_path)
        print(f"Moved: {filepath} -> {target_path}")


def scan_and_process():
    for root, dirs, files in os.walk(ROOT_DIR):

        # Skip already organized folder
        if os.path.abspath(root).startswith(os.path.abspath(OUTPUT_DIR)):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            move_file(full_path)


if __name__ == "__main__":
    scan_and_process()
