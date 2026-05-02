import os

# -------- CONFIG --------
ROOT_DIR = r"F:\toupload\organized"
DRY_RUN = False
# ------------------------


def log(msg):
    print(msg, flush=True)


def is_empty_folder(path):
    try:
        return len(os.listdir(path)) == 0
    except Exception:
        return False


def delete_empty_folders(root):
    removed_any = True

    # keep looping until no more deletions possible (handles nested empties)
    while removed_any:
        removed_any = False

        for current_root, dirs, files in os.walk(root, topdown=False):
            for d in dirs:
                folder_path = os.path.join(current_root, d)

                if is_empty_folder(folder_path):
                    if DRY_RUN:
                        log(f"[DRY RUN] Would delete: {folder_path}")
                    else:
                        try:
                            os.rmdir(folder_path)
                            log(f"[DELETED] {folder_path}")
                            removed_any = True
                        except Exception as e:
                            log(f"[SKIP] {folder_path} ({e})")


def scan():
    log(f"[START] Cleaning empty folders: {ROOT_DIR}")
    delete_empty_folders(ROOT_DIR)
    log("[DONE]")


if __name__ == "__main__":
    scan()
