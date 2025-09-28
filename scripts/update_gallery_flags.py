#!/usr/bin/env python3
"""
update_gallery_flags.py
- Reads gallery-data.js (JSON or `window.GALLERY_MEDIA_DATA = ...;`)
- Calls the same API as gallery.js to fetch check_flag1 per item (by file_hash)
- Writes only items with check_flag1 == "1" to new_jsondata_media.(js|json)
"""
import os
import re
import json
import time
import pathlib
from typing import Any, Dict, List

try:
    import requests
except ImportError:
    raise SystemExit("Please install requests: pip install requests")

INPUT_JSON = "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/assets/js/gal_data.json"
OUT_DIR = "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/assets/js"
OUT_JSON = os.path.join(OUT_DIR, "gallerydata.json")
OUT_JS = os.path.join(OUT_DIR, "gallerydata.js")
API_BASE = "https://test.svitua.se/db_tools/manage_attrib.php"



def read_gallery_data(path: str) -> Dict[str, Any]:
    """Read JSON"""
    # Read JSON not js
    with open(path, "r", encoding="utf-8") as f:        
        data = json.load(f)
    return data


def read_checkbox_state(file_hash: str, timeout: float = 8.0) -> str:
    """Call the API like gallery.js readCheckboxState(fileHash). Return "1" or "0"."""
    try:
        resp = requests.get(API_BASE, params={"file_hash": file_hash}, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("status") == "ok":
            val = payload.get("check_flag1")
            # Normalize truthy to "1"
            if isinstance(val, bool):
                return "1" if val else "0"
            if isinstance(val, (int, float)):
                return "1" if int(val) == 1 else "0"
            if isinstance(val, str):
                return "1" if val.strip() in ("1", "true", "True") else "0"
        return "0"
    except Exception:
        return "0"

def main_read_check_flag():
    t0 = time.time()
    try:
        data = read_gallery_data(INPUT_JSON)
    except Exception as e:
        print(f"✗ Failed to read input: {e}")
        return 1

    items: List[Dict[str, Any]] = data.get("media_files", [])
    total = len(items)
    updated = 0

    for item in items:
        file_hash = item.get("file_hash")
        if not file_hash:
            item["check_flag1"] = "0"
            continue
        state = read_checkbox_state(file_hash)
        item["check_flag1"] = state
        updated += 1

    # filter only selected
    filtered = [it for it in items if str(it.get("check_flag1", "0")) == "1"]
    out_data = {"media_files": filtered}

    os.makedirs(OUT_DIR, exist_ok=True)

    # write JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)

    # write JS wrapper
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write("window.NEW_JSONDATA_MEDIA = ")
        json.dump(out_data, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    took = int((time.time() - t0) * 1000)
    print(f"✓ Done. items={total}, updated={updated}, selected={len(filtered)}, time={took}ms")
    print(f"- JSON: {OUT_JSON}\n- JS:   {OUT_JS}")
    return 0

def delete_directory_elem_from_json():
    with open(OUT_JSON, "r", encoding="utf-8") as f:        
        data = json.load(f)
    
    items: List[Dict[str, Any]] = data.get("media_files", [])
    total = len(items)
    new_json_data = {}

    for item in items:
        # delete "directory" if present
        if isinstance(item, dict):
            item.pop('directory', None)

    # with open(OUT_JSON, "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    
        # write JS wrapper
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write("window.NEW_JSONDATA_MEDIA = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";\n")


def main() -> int:
   delete_directory_elem_from_json()




if __name__ == "__main__":
    raise SystemExit(main())
