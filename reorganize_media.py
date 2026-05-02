import os
import shutil
import re

# -------- CONFIG --------
ROOT_DIR = r"F:\toupload\organized"
DRY_RUN = False
# ------------------------


def log(msg):
    print(msg, flush=True)


def is_date_folder(name):
    # matches yyyy.mm.dd
    return re.match(r"^\d{4}\.\d{2}\.\d{2}$", name)


def get_month_folder(name):
    # yyyy.mm.dd -> yyyy.mm
    parts = name.split(".")
    return f"{parts[0]}.{parts[1]}"


def move_folder(src, dst):
    if DRY_RUN:
        log(f"[DRY RUN] {src} -> {dst}")
        return

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    log(f"[MOVED] {src} -> {dst}")


def scan():
    log(f"[START] {ROOT_DIR}")

    for item in os.listdir(ROOT_DIR):
        src_path = os.path.join(ROOT_DIR, item)

        if not os.path.isdir(src_path):
            continue

        if not is_date_folder(item):
            continue

        month_folder = get_month_folder(item)
        dst_dir = os.path.join(ROOT_DIR, month_folder)
        dst_path = os.path.join(dst_dir, item)

        move_folder(src_path, dst_path)

    log("[DONE] Restructure complete")


if __name__ == "__main__":
    scan()
