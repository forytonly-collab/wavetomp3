import os
import sys
import subprocess
import json
from pathlib import Path

# Handle Japanese/Unicode characters
sys.stdout.reconfigure(encoding='utf-8')

def load_config():
    """Reads the shared config file for the root path."""
    config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        print("❌ ERROR: 'config.json' not found in this folder.")
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("voice_work_path")
    except Exception as e:
        print(f"❌ ERROR: Could not read config.json: {e}")
        return None

def convert_and_cleanup(root_path):
    if not root_path:
        return

    print(f"🔍 Scanning: {root_path}")
    
    if not os.path.exists(root_path):
        print("!!! ERROR: VoiceWork folder not found. Check your config.json path.")
        return

    target_extensions = (".wav", ".m4a")

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.lower().endswith(target_extensions):
                source_path = os.path.normpath(os.path.join(dirpath, filename))
                file_base = os.path.splitext(filename)[0]
                mp3_path = os.path.normpath(os.path.join(dirpath, f"{file_base}.mp3"))

                if os.path.exists(mp3_path):
                    continue

                print(f"📦 Processing: {filename}")
                
                # Using double quotes to handle spaces in Windows paths
                # -y overwrites existing, -ab 192k sets bitrate
                cmd = f'ffmpeg -i "{source_path}" -y -ab 192k -loglevel error "{mp3_path}"'

                try:
                    # Run via shell to handle Windows special characters/paths
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        os.remove(source_path)
                        print(f"✅ Success & Deleted: {filename}")
                    else:
                        print(f"⚠️ FFmpeg Error on {filename}: {result.stderr}")
                except Exception as e:
                    print(f"❌ System Error on {filename}: {e}")

# --- Execution ---
print("--- Final Robust Converter Started ---")

# Pull the path from our "secret" config
root_folder = load_config()

if root_folder:
    convert_and_cleanup(root_folder)
    print("--- All Tasks Finished ---")
else:
    print("--- Task Aborted: Missing Config ---")

input("Press Enter to exit...")