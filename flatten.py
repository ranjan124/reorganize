import os
import shutil

# -------- CONFIG --------
ROOT_DIR = r"F:\toupload\organized"
DRY_RUN = False
# ------------------------


def log(msg):
    print(msg, flush=True)


def safe_move(src, dst):
    if DRY_RUN:
        log(f"[DRY RUN] {src} -> {dst}")
        return

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    log(f"[MOVED] {dst}")


def process_day_folder(day_folder_path, month_folder):
    day_name = os.path.basename(day_folder_path)

    images_path = os.path.join(day_folder_path, "images")
    videos_path = os.path.join(day_folder_path, "videos")

    # ---------------- IMAGES ----------------
    if os.path.exists(images_path):
        images = sorted([
            f for f in os.listdir(images_path)
            if os.path.isfile(os.path.join(images_path, f))
        ])

        for idx, img in enumerate(images, start=1):
            ext = os.path.splitext(img)[1].lower()
            new_name = f"{day_name}-image-{idx:03d}{ext}"

            src = os.path.join(images_path, img)
            dst = os.path.join(month_folder, new_name)

            safe_move(src, dst)

    # ---------------- VIDEOS ----------------
    if os.path.exists(videos_path):
        videos = sorted([
            f for f in os.listdir(videos_path)
            if os.path.isfile(os.path.join(videos_path, f))
        ])

        for idx, vid in enumerate(videos, start=1):
            ext = os.path.splitext(vid)[1].lower()
            new_name = f"{day_name}-video-{idx:03d}{ext}"

            src = os.path.join(videos_path, vid)
            dst = os.path.join(month_folder, new_name)

            safe_move(src, dst)


def scan():
    log(f"[START] {ROOT_DIR}")

    for month in os.listdir(ROOT_DIR):
        month_path = os.path.join(ROOT_DIR, month)

        if not os.path.isdir(month_path):
            continue

        # yyyy.mm check
        if month.count(".") != 1:
            continue

        for day in os.listdir(month_path):
            day_path = os.path.join(month_path, day)

            if not os.path.isdir(day_path):
                continue

            # yyyy.mm.dd check
            if day.count(".") != 2:
                continue

            log(f"[PROCESS] {day}")

            process_day_folder(day_path, month_path)

    log("[DONE]")


if __name__ == "__main__":
    scan()
