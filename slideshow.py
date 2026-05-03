import os
import subprocess
import time

# CONFIG
BASE_DIR = r"F:\toupload\organized"
FFMPEG = r"D:\playground\videosplitter\media-tool\ffmpeg.exe"
DURATION = 3  # seconds per image

def get_date_from_filename(filename):
    try:
        y, m, d = filename.split("-")[0].split(".")
        return f"{d}.{m}.{y}"  # <-- changed format
    except:
        return "unknown"

def create_slideshow(images, output_file):
    inputs = []
    filters = []

    for i, (img, date) in enumerate(images):
        inputs += ["-loop", "1", "-t", str(DURATION), "-i", img]

        filters.append(
            f"[{i}:v]"
            f"scale=1280:720:force_original_aspect_ratio=decrease,"
            f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,"
            f"drawtext=text={date}:"
            f"fontcolor=white:fontsize=36:"
            f"x=w-tw-20:y=h-th-20:"
            f"box=1:boxcolor=black@0.5:boxborderw=10"
            f"[v{i}]"
        )

    concat_inputs = "".join([f"[v{i}]" for i in range(len(images))])
    filter_complex = ";".join(filters) + f";{concat_inputs}concat=n={len(images)}:v=1:a=0[v]"

    cmd = [
        FFMPEG,
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-vsync", "2",
        "-pix_fmt", "yuv420p",
        "-y",
        output_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("[FFMPEG ERROR]")
        print(result.stderr)
        return False

    return True

def main():
    print("[START]", BASE_DIR)
    print("[INFO] Using FFmpeg:", FFMPEG)

    total_start = time.time()

    for month in sorted(os.listdir(BASE_DIR)):
        month_path = os.path.join(BASE_DIR, month)
        if not os.path.isdir(month_path):
            continue

        images = []
        for file in sorted(os.listdir(month_path)):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                full_path = os.path.join(month_path, file)
                date = get_date_from_filename(file)
                images.append((full_path, date))
                print("[IMG]", full_path, "->", date)

        if not images:
            continue

        print(f"[MONTH] {month} -> {len(images)} images")

        output_file = os.path.join(month_path, f"{month}-slideshow.mp4")
        print("[CREATE]", output_file)

        start = time.time()
        success = create_slideshow(images, output_file)
        end = time.time()

        if success:
            print(f"[TIME] {month} took {round(end - start, 2)} sec")

    print(f"[TOTAL TIME] {round(time.time() - total_start, 2)} sec")
    print("[DONE]")

if __name__ == "__main__":
    main()
