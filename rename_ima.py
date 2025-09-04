#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime
import argparse
import sys

# Pattern to match e.g. "ChatGPT Image Aug 22, 2025, 12_45_12 PM.png"
DATE_RE = re.compile(
    r'([A-Za-z]{3,}\s+\d{1,2},\s*\d{4},\s*\d{1,2}_\d{1,2}_\d{1,2}\s*(?:AM|PM)?)',
    re.IGNORECASE,
)
DT_FMT_SHORT = "%b %d, %Y, %I_%M_%S %p"   # "Aug 22, 2025, 12_45_12 PM"
DT_FMT_LONG = "%B %d, %Y, %I_%M_%S %p"    # "August 22, 2025, 12_45_12 PM"

# Pattern matching already numbered files like 0001.png or 00123.jpg (capture number)
NUM_RE = re.compile(r'^0*(\d+)$')

# Allowed image extensions (lowercase)
ALLOWED_EXT = {'.png', '.jpg', '.jpeg'}

def parse_date_from_name(name: str):
    m = DATE_RE.search(name)
    if not m:
        return None
    s = re.sub(r'\s+', ' ', m.group(1).strip())
    for fmt in (DT_FMT_SHORT, DT_FMT_LONG):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def detect_existing_numbers(files):
    """
    Return dict mapping integer index -> Path for files whose stem is a zero-padded number
    and whose extension is in ALLOWED_EXT. Example: 0001.png -> 1
    """
    existing = {}
    for f in files:
        if f.suffix.lower() not in ALLOWED_EXT:
            continue
        stem = f.stem  # name without suffix
        m = NUM_RE.match(stem)
        if m:
            try:
                num = int(m.group(1))
            except ValueError:
                continue
            existing[num] = f
    return existing

def main(folder: Path, dry_run: bool):
    if not folder.exists() or not folder.is_dir():
        print("Folder does not exist or is not a directory:", folder)
        sys.exit(1)

    # Consider only files with allowed image extensions
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXT]
    if not files:
        print("No image files (.png/.jpg/.jpeg) found in folder.")
        return

    existing_numbers = detect_existing_numbers(files)
    existing_indices = sorted(existing_numbers.keys())
    next_index = (max(existing_indices) + 1) if existing_indices else 1

    # Files that are already numbered (we'll preserve them)
    numbered_files_set = set(existing_numbers.values())

    # Remaining image files (not already numbered)
    remaining = [p for p in files if p not in numbered_files_set]

    # Parse dates for remaining filenames
    parsed = []
    others = []
    for f in remaining:
        dt = parse_date_from_name(f.name)
        if dt:
            parsed.append((f, dt))
        else:
            others.append(f)

    parsed.sort(key=lambda x: x[1])          # by date ascending
    others.sort(key=lambda p: p.name.lower())# alphabetic for remaining

    ordered_new = [p for p, _ in parsed] + others

    total_final = len(existing_indices) + len(ordered_new)
    pad = max(4, len(str(total_final)))  # at least 4 digits

    # Build mapping for renames. We will not rename already-numbered files.
    rename_plan = []  # tuples (src Path, final Path)
    for idx, src in enumerate(ordered_new, start=next_index):
        new_basename = f"{idx:0{pad}d}{src.suffix.lower()}"
        final_path = folder / new_basename
        rename_plan.append((src, final_path))

    # Check for collisions: ensure no new target overwrites an existing preserved numbered file
    final_targets = {t for _, t in rename_plan}
    for num_idx, existing_path in existing_numbers.items():
        target_name = folder / f"{num_idx:0{pad}d}{existing_path.suffix.lower()}"
        if target_name in final_targets:
            print("Collision detected: a rename target would overwrite an existing numbered file:", target_name.name)
            sys.exit(1)

    # Ensure no duplicate final targets
    if len(final_targets) != len(rename_plan):
        print("Internal error: duplicate target names detected.")
        sys.exit(1)

    # Two-step rename: first to temporary names, then to final names
    temp_suffix = ".duckrenametemp"
    temp_plan = []
    for src, final in rename_plan:
        temp = src.with_name(final.name + temp_suffix)
        temp_plan.append((src, temp, final))

    # Ensure no temp name collides with existing files
    for _, temp, _ in temp_plan:
        if temp.exists():
            print("Temp name already exists:", temp.name)
            sys.exit(1)

    # Dry-run printout
    if dry_run:
        print(f"Existing numbered files preserved: {len(existing_indices)} (next index {next_index})")
        for num in existing_indices:
            p = existing_numbers[num]
            print(f"KEEP: {p.name}")
        for src, temp, final in temp_plan:
            print(f"RENAME: {src.name} -> {final.name} (temp {temp.name})")
        print("DRY RUN complete.")
        return

    # Perform renames: step 1 -> temp
    for src, temp, _ in temp_plan:
        src.rename(temp)

    # Step 2 -> final
    for _, temp, final in temp_plan:
        temp.rename(final)

    print(f"Done. Preserved {len(existing_indices)} numbered files; renamed {len(temp_plan)} new image files. Total = {total_final}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Incrementally rename new PNG/JPG/JPEG files to sequential zero-padded numbers, preserving existing numbered image files."
    )
    ap.add_argument("folder", help="Folder to process (required)")
    ap.add_argument("--dry-run", action="store_true", help="Show actions without performing renames")
    args = ap.parse_args()
    main(Path(args.folder), args.dry_run)
