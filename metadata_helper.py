# metadata_helper.py
import os
import json
from PIL import Image

IMAGE_DIR = "images"
OUTPUT_FILE = os.path.join(IMAGE_DIR, "metadata.json")
EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")

def generate_metadata():
    data = []
    if not os.path.exists(IMAGE_DIR):
        print(f"⚠️ No folder: {IMAGE_DIR}")
        return []
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(EXTS):
            filepath = os.path.join(IMAGE_DIR, filename)
            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                    data.append({
                        "filename": filename,
                        "width": width,
                        "height": height
                    })
            except Exception as e:
                print(f"⚠️ Could not read {filename}: {e}")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Metadata updated: {OUTPUT_FILE} ({len(data)} images)")
    return data
