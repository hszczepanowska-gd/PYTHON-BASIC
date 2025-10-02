import requests
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
import time

load_dotenv()
API_KEY = os.environ.get("NASA_API_KEY")
APOD_ENDPOINT = 'https://api.nasa.gov/planetary/apod'
OUTPUT_IMAGES = './output'


def get_apod_metadata(start_date: str, end_date: str, api_key: str) -> list:
    response = requests.get(
        f"{APOD_ENDPOINT}?api_key={api_key}&start_date={start_date}&end_date={end_date}"
    )
    return response.json()

def download_image(day_metadata: dict):
    img = requests.get(day_metadata["url"])

    file_ext = day_metadata["url"].split(".")[-1]
    if file_ext not in ["jpg", "jpeg", "png", "gif"]:
        file_ext = "jpg"

    with open(f"{OUTPUT_IMAGES}/{day_metadata['date']}.{file_ext}", "wb") as f:
        f.write(img.content)

def download_apod_images(metadata: list):
    files_to_download = [day for day in metadata if day["media_type"] == "image"]
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(download_image, files_to_download)

    end_time = time.time()
    print(f"Downloaded {len(files_to_download)} images in {end_time - start_time:.2f} seconds.")

def main():
    metadata = get_apod_metadata(
        start_date='2021-08-01',
        end_date='2021-09-30',
        api_key=API_KEY,
    )
    download_apod_images(metadata=metadata)


if __name__ == '__main__':
    if not os.path.exists(OUTPUT_IMAGES):
        os.makedirs(OUTPUT_IMAGES)
    main()
