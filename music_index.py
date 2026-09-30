import credentials
from pathlib import Path
import json
import requests
import os
import shutil
import numpy as np
import cv2
from typing import List, Tuple
import subprocess
import argparse

upload_to = os.path.join("Resources", "Music", "Index")
index_name = "music_index.json"
index_path = os.path.join("data", "MusicIndex", index_name)
upload_url = "https://neocities.org/api/upload"
neocities_header = {"Authorization": f"Bearer {credentials.neocities_api}"}
albums_directory = credentials.music_path
supported_audio_formats = ["opus", "mp3", "flac", "m4a"]
supported_image_formats = ["jpg", "jpeg", "png", "webp", "webm"]


class MusicIndex:
    def __init__(self):
        # Settings that determine how the update is run.
        # self.update_art = True
        self.update_songs = True  # Count, duration
        self.update_average_color = True
        self.dont_upload = False
        # self.update_album_metadata = True  # Album, artist, release date

        self.index = {}
        # Info that should only be used in this program, such as getting local file paths.
        self.local_index = {}
        self.no_art = []
        self.missing_metadata = []
        self.unrecognized_file = []
        # TODO: Check to make sure all existing_index values are also found.

    def do_index(self, start, album_index_limit):
        album_num = 0
        for artist in get_directories(albums_directory):
            albums = get_directories(str(artist))
            for album in albums:
                if start > 0:
                    start -= 1
                    continue
                album_num += 1
                if album_num % 10 == 0:
                    print(f"Indexed {album_num} albums")
                # album_name = album.stem
                # We need art to display it on the website. Mandatory check.
                album_art = self.get_album_art(album)
                if album_art is None:
                    self.no_art.append(album)
                    continue

                album_indexed = False
                artist_name = album_name = date = ""
                duration_total = 0
                average_color = [0, 0, 0]
                song_count = 0
                for song in album.iterdir():
                    # Check if this is an audio file. If it's an unrecognized format, report this.
                    if song.suffix[1:] not in supported_audio_formats:
                        if song.suffix[1:] not in supported_image_formats:
                            self.unrecognized_file.append(song)
                            continue
                        continue

                    metadata = self.get_metadata(str(song))
                    try:
                        duration = float(metadata["format"]["duration"])
                        if not album_indexed:
                            # TODO: Make date optional
                            if "tags" in metadata["format"]:
                                artist_name = metadata["format"]["tags"]["artist"]
                                album_name = metadata["format"]["tags"]["album"]
                                date = metadata["format"]["tags"]["date"]
                            else:
                                # we're in deep if it's not in the first stream
                                artist_name = metadata["streams"][0]["tags"]["ARTIST"]
                                album_name = metadata["streams"][0]["tags"]["ALBUM"]
                                date = metadata["streams"][0]["tags"]["DATE"]
                            album_indexed = True
                    except KeyError:
                        # We can broadly assume if one song doesn't have the right metadata, none of them do.
                        self.missing_metadata.append(song)
                        song_count = 0
                        duration_total = 0
                        break

                    if not self.update_songs or not album_indexed:
                        break
                    duration_total += duration
                    song_count += 1

                if not album_indexed:
                    continue
                # Using the names as filename caused issues for neocities because of ellipses.
                album_art_name = f"{hash(artist_name + album_name)}{album_art.suffix}"
                server_art_path = os.path.join(upload_to, album_art_name)
                if self.update_average_color:
                    average_color = get_average_color(str(album_art))
                # Copy art to directory. TODO: Might be able to just upload directly from source.
                # shutil.copyfile(album_art, os.path.join(art_path, album_art_name))
                self.set_index_entry(album, artist_name, album_name, album_art, server_art_path, average_color, date, duration_total, song_count)

            if album_num >= album_index_limit:
                break
        print("====== Unrecognized =======")
        print(self.unrecognized_file)
        print("====== Missing metadata =======")
        print(self.missing_metadata)
        print("====== No art =======")
        print(self.no_art)
        print("=============")
        self.write_index()
        if not self.dont_upload:
            self.upload_index()
            self.upload_art()

    def set_index_entry(self, local_path, artist, album, local_art_path, server_art_path, average_color, release_date, duration, song_count):
        hashed_value = hash(local_path)
        self.local_index[hashed_value] = {
            "album_path": local_path,
            "art_path": local_art_path,
        }

        self.index[hashed_value] = {
            "hash": hashed_value,
            "artist": artist,
            "album": album,
            "art": server_art_path,
            "average_color": average_color,
            "release_date": release_date,
            "duration": duration,
            "song_count": song_count,
            # TODO: Date I got file? Might not work with bandcamp.
        }

    @staticmethod
    def get_metadata(path: str):
        # res = subprocess.check_output(["ffprobe", "-i", path, "-show_entries", "format=duration", "-show_entries", "format_tags=album,artist,date", "-v", "quiet", "-of", "default=nk=1:nw=1"])

        # json format is slower to work with, but it's a lot more error resistant having this much info and using established libraries.
        # we need to check both the "format" and "stream"... things, because different formats place it in different spots. opus does streams, mp3 does format.
        res = subprocess.check_output(["ffprobe", "-i", path, "-show_entries", "format=duration", "-show_entries", "format_tags=album,artist,date", "-show_entries", "stream_tags=album,artist,date", "-v", "quiet", "-of", "json=c=1"]).decode("utf-8")
        return json.loads(res)

    def write_index(self):
        full_index = {
            "metadata": {
                "omitted": len(self.no_art) + len(self.missing_metadata)
            },
            "index": self.index
        }
        with open(index_path, "w") as fp:
            json.dump(full_index, fp)

    def upload_index(self):
        push_location = os.path.join(upload_to, index_name)
        to_push = [(push_location, index_path)]
        upload_files(to_push)

    def upload_art(self):
        to_push = []
        for album in self.index:
            album_index = self.index[album]
            album_local = self.local_index[album]
            to_push.append((album_index["art"], album_local["art_path"]))
        # Neocities gets upset if I try to do too many at once. Chunking the list makes it okay.
        push_chunk_size = 50
        i = 0
        while i <= len(to_push):
            files_chunk = to_push[i:i + push_chunk_size]
            i += push_chunk_size
            upload_files(files_chunk)

    @staticmethod
    def get_album_art(path: Path):
        # simple, quick, prone to breaking
        for extension in supported_image_formats:
            p = path / ("album." + extension)
            if p.exists():
                return p
        return None

class UnrecognizedFile(Exception):
    pass
class MissingMetadata(Exception):
    pass

def upload_files(files: List[Tuple[str, str]]):
    print(f"Pushing: {repr(files)}")

    # Get the file data from the path, and write it to the chunk
    files_data = {pair[0]: open(pair[1], 'rb') for pair in files}
    request = requests.post(upload_url, headers=neocities_header, files=files_data)
    if request.status_code == 200:
        return request.status_code

    print(f"Failed to post to {upload_url}\nstatus code: {request.status_code}\nresponse: {request.text}")
    return request.status_code

    
def get_directories(path: str):
    return [f for f in Path(path).iterdir() if f.is_dir()]


def get_average_color(img_path: str):
    # Load the image
    im = cv2.imread(img_path)
    # Calculate mean of green area
    return np.mean(im, axis=(0, 1)).tolist()


def extract_all_artwork():
    for artist in get_directories(albums_directory):
        did_something = False
        for album in get_directories(str(artist)):
            has_art = False
            # Check if artwork already exists.
            for file_format in supported_image_formats:
                if len(list(album.glob(f"*.{file_format}"))) > 0:
                    has_art = True
                    break
            if has_art:
                continue

            songs = [f for f in album.iterdir() if f.suffix[1:] in supported_audio_formats]
            try:
                print(subprocess.check_output(["kid3-cli", "-c", "select", str(songs[0]), "-c", f'get picture:"{os.path.join(album, "album.png")}"']))
                print("Ran on: " + str(album))
            except:
                print("Couldn't get picture from album: " + str(album))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('start', nargs='?', type=int, default=0,
                        help="Album number to start from. This is an arbitrary order, and only useful to continue a partial index.")
    parser.add_argument('count', nargs='?', type=int, default=9999, help="Number of albums to index")
    parser.add_argument('-d', "--dry", action='store_true', help="Don't upload result.")
    # parser.add_argument('-v', '--verbose',
    #                     action='store_true')  # on/off flag
    args = parser.parse_args()
    mi = MusicIndex()
    mi.dont_upload = args.dry
    mi.do_index(args.start, args.count)
    return
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
                "average_color": get_average_color(str(album_art)),
                # "release_date":
                # "duration"
            }
            music_index.append(album_data)

    print(f"Did not index {len(not_indexed)}")
    #     print(not_indexed)
    # TODO: Clear remote directory
    with open(os.path.join(upload_from, "music_index.json"), "w") as fp:
        json.dump(music_index, fp)
    push_folder(upload_from, upload_to)


if __name__ == "__main__":
    main()