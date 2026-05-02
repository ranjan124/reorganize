import os
import subprocess

# -------- CONFIG --------
ROOT_DIR = r"F:\toupload\temp"

IMAGE_EXT = {".jpg", ".jpeg", ".png"}
DURATION_PER_IMAGE = 5

DRY_RUN = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(BASE_DIR, "media-tool", "ffmpeg.exe")
# ------------------------


def log(msg):
    print(msg, flush=True)


def check_ffmpeg():
    return os.path.exists(FFMPEG_PATH)


def is_image_file(name):
    return "-image-" in name and os.path.splitext(name)[1].lower() in IMAGE_EXT


def extract_date(filename):
    return filename.split("-image-")[0]


def collect_images(folder):
    images = []
    for f in os.listdir(folder):
        if is_image_file(f):
            images.append(os.path.join(folder, f))
    return sorted(images)


def build_filter(images):
    """
    Create per-image overlays using concat + drawtext index trick
    """

    filters = []

    for i, img in enumerate(images):
        name = os.path.basename(img)
        date = extract_date(name)

        filters.append(
            f"[{i}:v]scale=trunc(iw/2)*2:trunc(ih/2)*2,"
            f"drawtext=text='{date}':"
            f"fontcolor=white:fontsize=36:"
            f"x=w-tw-20:y=h-th-20:"
            f"box=1:boxcolor=black@0.5:boxborderw=10[v{i}]"
        )

    concat_inputs = "".join([f"[v{i}]" for i in range(len(images))])

    filters.append(f"{concat_inputs}concat=n={len(images)}:v=1:a=0[v]")

    return ";".join(filters)


def create_slideshow(folder, images):
    month_name = os.path.basename(folder)
    output = os.path.join(folder, f"{month_name}-slideshow.mp4")

    if not images:
        log(f"[SKIP] {month_name} -> no images")
        return

    # build ffmpeg inputs
    cmd = [FFMPEG_PATH, "-y"]

    for img in images:
        cmd += ["-loop", "1", "-t", str(DURATION_PER_IMAGE), "-i", img]

    filter_complex = build_filter(images)

    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-r", "30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output
    ]

    if DRY_RUN:
        log(f"[DRY RUN] {output} ({len(images)} images)")
        return

    log(f"[CREATE] {output} ({len(images)} images)")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log("[FFMPEG ERROR]")
        log(result.stderr)
    else:
        log(f"[DONE] {output}")


def process_month(folder):
    images = collect_images(folder)

    log(f"[MONTH] {os.path.basename(folder)} -> {len(images)} images")

    for img in images:
        log(f"[IMG] {os.path.basename(img)} -> {extract_date(os.path.basename(img))}")

    create_slideshow(folder, images)


def scan():
    log(f"[START] {ROOT_DIR}")

    if not check_ffmpeg():
        log(f"[ERROR] FFmpeg not found: {FFMPEG_PATH}")
        return

    for item in os.listdir(ROOT_DIR):
        path = os.path.join(ROOT_DIR, item)
        if os.path.isdir(path):
            process_month(path)

    log("[DONE]")


if __name__ == "__main__":
    scan()
