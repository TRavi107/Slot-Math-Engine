
def print_progress(completed, total):
    percent = int((completed / total) * 100)
    filled  = percent // 5          # 20 blocks = 100%
    bar     = "█" * filled + "-" * (20 - filled)
    print(f"  [{bar}] {percent}%  ({completed:,}/{total:,} spins)", flush=True)