import credentials
from pathlib import Path
import json
import requests
import os

def main():
    upload_from = os.path.join("data", "MusicIndex")
    
    not_indexed_count = 0
    covers_to_copy = []
    music_index = []
    # temp directory for album covers before being pushed
    artists = get_directories(credentials.music_path)
    for artist in artists:
        # TODO: Read metadata from tracks instead
        artist_name = artist.stem
        albums = get_directories(credentials.music_path)
        for album in albums:
            album_name = album.stem
            album_art = get_album_art(album)
            if album_art is None:
                not_indexed_count += 1
                continue
            new_name = f"{artist_name}-{album_name}-{album_art.name}"
            # Copy art to directory
            os.link(album_art, os.join(upload_from, new_name))
            
            album_data = {
                "artist": artist_name,
                "album": album_name,
                "art": new_name,
                #"release_date":
                #"duration" 
            }
            music_index.append(album_data)
            
    # TODO: Clear remote directory
    upload_to = os.path.join("Resources", "Music", "Index")
    json.dump(music_index, os.join(upload_from, "music_index.json"))
    # scale_images(covers_to_copy)
    # push_folder(upload_from, upload_to)
    
    
def get_directories(path: Path):
    return [f for f in path if f.is_dir()]
    

def get_album_art(path: Path):
    # simple, quick, prone to breaking
    to_check = ["jpg", "png"]
    for extension in to_check:
        p = path / ("album." + extension)
        if p.exists():
            return p
    return None


def scale_images(paths):
    # TODO: Make thumbnail sizes of the images so they load faster.
    pass
     

def push_data(file_data: string, d_to: string):
    url = "https://neocities.org/api/upload"
    headers = {"Authorization": f"Bearer {credentials.neocities_api}"}
    files = {f"{d_to}": file_data}
    request = requests.post(url, headers=headers, files=files)

    if request.status_code == 200:
        logger.info(f"Uploaded {upload_location} to {url} successfully.")
        response.status_code = 200
        return response
    
    response.status_code = 500
    logger.error(f"Failed to post {upload_location} to {url}\nstatus code: {request.status_code}\nresponse: {request.text}")


def push_folder(d_from, d_to):
    url = "https://neocities.org/api/upload"
    headers = {"Authorization": f"Bearer {credentials.neocities_api}"}
    files_to_push = [f for f in d_from if f.is_file()]
    form_data = {}
    for file in file_to_push:
        to = os.join(d_to, file.name)
        form_data[file.path] = to
    
    request = requests.post(url, headers=headers, data=form_data)

    if request.status_code == 200:
        logger.info(f"Uploaded folder {d_from} to {url} successfully.")
        response.status_code = 200
        return response
    
    response.status_code = 500
    logger.error(f"Failed to post {upload_location} to {url}\nstatus code: {request.status_code}\nresponse: {request.text}")
