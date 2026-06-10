from datetime import datetime, timedelta, timezone
import requests
import zipfile
import io
from pathlib import Path

out_dir = Path("gdelt_downloads")
out_dir.mkdir(exist_ok=True)

base_url = "http://data.gdeltproject.org/gdeltv2"

now = datetime.now(timezone.utc)
start = now - timedelta(days=1)

current = start.replace(minute=(start.minute // 15) * 15, second=0, microsecond=0)

while current <= now:
    timestamp = current.strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}.gkg.csv.zip"
    url = f"{base_url}/{filename}"

    print("Downloading", filename)

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            zip_path = out_dir / filename
            zip_path.write_bytes(response.content)
            print("Saved", zip_path)
        else:
            print("Skipped", filename, response.status_code)

    except requests.RequestException as e:
        print("Failed", filename, e)

    current += timedelta(minutes=15)