import credentials
from pathlib import Path
import json
import requests
import os
import shutil

def main():
    upload_from = os.path.join("data", "MusicIndex")
    
    not_indexed = []
    covers_to_copy = []
    music_index = []
    # temp directory for album covers before being pushed
    artists = get_directories(credentials.music_path)
    for artist in artists:
        # TODO: Read metadata from tracks instead
        artist_name = artist.stem
        albums = get_directories(artist)
        for album in albums:
            album_name = album.stem
            album_art = get_album_art(album)
            if album_art is None:
                not_indexed.append(album)
                continue
            new_name = f"{artist_name}-{album_name}-{album_art.name}"
            # Copy art to directory
            shutil.copyfile(album_art, os.path.join(upload_from, new_name))
            
            album_data = {
                "artist": artist_name,
                "album": album_name,
                "art": new_name,
                #"release_date":
                #"duration" 
            }
            music_index.append(album_data)
            
    print(f"Did not index {len(not_indexed)}")
#     print(not_indexed)
    # TODO: Clear remote directory
    upload_to = os.path.join("Resources", "Music", "Index")
    with open(os.path.join(upload_from, "music_index.json"), "w") as fp:
        json.dump(music_index, fp)
    # scale_images(covers_to_copy)
    push_folder(upload_from, upload_to)
    
    
def get_directories(path: Path):
    return [f for f in Path(path).iterdir() if f.is_dir()]
    

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
     

def push_data(file_data: str, d_to: str):
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
    d_from = Path(d_from)
    d_to = Path(d_to)
    url = "https://neocities.org/api/upload"
    headers = {"Authorization": f"Bearer {credentials.neocities_api}"}
    local_files = [f for f in d_from.iterdir() if f.is_file()]
    
    files_to_push = []
    for file in local_files:
        push_location = os.path.join(d_to, file.name)
        tup = (str(push_location), str(file))
        files_to_push.append(tup)

#     files_to_push = [
#     ("Resources/Music/Index/music_index.json", "data/MusicIndex/music_index.json"),
#     ("Resources/Music/Index/Aesop Rock-Black Hole Superette-album.jpg", "data/MusicIndex/Aesop Rock-Black Hole Superette-album.jpg")
#     ]
    # Push the files in chunks, so if any cause errors I can narrow it down.
    # TODO: Play with this number to see what neocities is okay with.
    # It has a 100MB upload limit, but that wasn't the cap I was hitting.
    push_chunk_size = 25
    i = 0
    while i <= len(files_to_push):
        files_chunk = files_to_push[i:i+push_chunk_size]
        i += push_chunk_size
        print(f"Pushing: {repr(files_chunk)}")
        
        # Get the file data from the path, and write it to the chunk
        files_data = {pair[0]: open(pair[1], 'rb') for pair in files_chunk}
        request = requests.post(url, headers=headers, files=files_data)
        if request.status_code == 200:
#             print(f"Uploaded folder {d_from} to {url} successfully.")
            request.status_code = 200
            continue
        
#         request.status_code = 500
        print(f"Failed to post {d_from} to {url}\nstatus code: {request.status_code}\nresponse: {request.text}")
        return


if __name__ == "__main__":
    main()