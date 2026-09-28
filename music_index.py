import credentials
from pathlib import Path
import json

def main():
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
            # TODO: Album art
            data = {
                "artist": artist_name,
                "album": album_name,
                "art": album_art
            }
            
    scale_images(covers_to_copy)
    save_data(music_index)
    push_data()
    
    
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
     

def save_data(data, d_to):
    # TODO
    pass


def push_data(d_from, d_to):
    # TODO: Take from views.py
    pass