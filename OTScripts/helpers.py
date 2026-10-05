import requests
from typing import List, Tuple, BinaryIO, Dict
import credentials

def upload_file_paths(files: List[Tuple[str, str]]):
    # Get the file data from the path, and write it to the chunk
    files_data = {pair[0]: open(pair[1], 'rb') for pair in files}
    return upload_file_data(files_data)


def upload_file_data(files: Dict[str, BinaryIO|str]):
    print(f"Pushing: {repr(files)}")
    upload_url = "https://neocities.org/api/upload"
    neocities_header = {"Authorization": f"Bearer {credentials.neocities_api}"}

    request = requests.post(upload_url, headers=neocities_header, files=files)
    if request.status_code == 200:
        return request.status_code

    print(f"Failed to post to {upload_url}\nstatus code: {request.status_code}\nresponse: {request.text}")
    return request.status_code