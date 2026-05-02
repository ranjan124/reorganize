import os
import subprocess

# -------- CONFIG --------
ROOT_DIR = r"F:\toupload\temp"

IMAGE_EXT = {".jpg", ".jpeg", ".png"}
DURATION_PER_IMAGE = 5
DRY_RUN = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_FFMPEG = os.path.join(BASE_DIR, "media-tool", "ffmpeg.exe")
# ------------------------


def log(msg):
    print(msg, flush=True)


def get_ffmpeg():
    """
    Use local ffmpeg if exists, otherwise fallback to system ffmpeg
    """
    if os.path.exists(LOCAL_FFMPEG):
        return LOCAL_FFMPEG
    return "ffmpeg"


FFMPEG = get_ffmpeg()


def is_image_file(name):
    return "-image-" in name and os.path.splitext(name)[1].lower() in IMAGE_EXT


def extract_date(filename):
    return filename.split("-image-")[0]


def collect_images(folder):
    images = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if is_image_file(f)
    ]
    return sorted(images)


def build_filter(images):
    """
    Normalize ALL images to same size BEFORE concat
    """

    filters = []

    for i, img in enumerate(images):
        name = os.path.basename(img)
        date = extract_date(name)

        filters.append(
            f"[{i}:v]"
            f"scale=1280:720:force_original_aspect_ratio=decrease,"
            f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
            f"format=yuv420p,"
            f"drawtext=text='{date}':"
            f"fontcolor=white:fontsize=36:"
            f"x=w-tw-20:y=h-th-20:"
            f"box=1:boxcolor=black@0.5:boxborderw=10"
            f"[v{i}]"
        )

    concat_inputs = "".join([f"[v{i}]" for i in range(len(images))])

    filters.append(
        f"{concat_inputs}concat=n={len(images)}:v=1:a=0[v]"
    )

    return ";".join(filters)


def create_slideshow(folder, images):
    month_name = os.path.basename(folder)
    output = os.path.join(folder, f"{month_name}-slideshow.mp4")

    if not images:
        log(f"[SKIP] {month_name} -> no images")
        return

    cmd = [FFMPEG, "-y"]

    # inputs
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

    if FFMPEG == "ffmpeg":
        log("[INFO] Using system FFmpeg")
    else:
        log(f"[INFO] Using local FFmpeg: {LOCAL_FFMPEG}")

    for item in os.listdir(ROOT_DIR):
        path = os.path.join(ROOT_DIR, item)
        if os.path.isdir(path):
            process_month(path)

    log("[DONE]")


if __name__ == "__main__":
    scan()
