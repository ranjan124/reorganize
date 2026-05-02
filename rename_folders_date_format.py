import os
import re
import shutil

# -------- CONFIG --------
ROOT_DIR = r"F:\toupload\organized"  # CHANGE THIS
DRY_RUN = False  # Set False to actually rename
# ------------------------


DATE_PATTERN = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")


def convert_folder_name(folder_name):
    match = DATE_PATTERN.match(folder_name)
    if not match:
        return None

    day, month, year = match.groups()
    return f"{year}.{month}.{day}"


def rename_folders():
    for item in os.listdir(ROOT_DIR):
        old_path = os.path.join(ROOT_DIR, item)

        if not os.path.isdir(old_path):
            continue

        new_name = convert_folder_name(item)
        if not new_name:
            continue

        new_path = os.path.join(ROOT_DIR, new_name)

        # Avoid overwrite
        if os.path.exists(new_path):
            print(f"[SKIP - EXISTS] {new_path}")
            continue

        if DRY_RUN:
            print(f"[DRY RUN] {old_path} -> {new_path}")
        else:
            print(f"Renaming: {old_path} -> {new_path}")
            shutil.move(old_path, new_path)


if __name__ == "__main__":
    rename_folders()
