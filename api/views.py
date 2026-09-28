from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import re
from time import time
import math
import logging
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import BadRequest
import requests
import credentials
import os
from typing import Dict

logger = logging.getLogger(__name__)

# Values expected: alias, website, message, image, location. append unix time

# TODO: Image parsing and uploading
# TODO: Sprite selection
@csrf_exempt  # TODO: remove this, ig.
def guestbook(request):
    logger.info("Received guestbook request.")
    response = HttpResponse()
    response.status_code = 500
    if request.method != "POST":
        logger.info("Refused guestbook request: Request was not POST.")
        response.status_code = 405
        return response
    
    # TODO: Get list of messages from website to compare positions against.
    guestbook_entries = {}
    try:
        guestbook_entries = fetch_guestbook()
    except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError):
        response.status_code = 500
        return response

    guestbook_request = None
    try:
        guestbook_request = parse_guestbook_request(request)
    except BadRequest:
        response.status_code = 400
        return response
    
    file_data = json.dumps({guestbook_request.id: guestbook_request.to_dict()})
    url = "https://neocities.org/api/upload"
    headers = {"Authorization": f"Bearer {credentials.neocities_api}"}
    filename = f"entry-{guestbook_request.id}.json"
    upload_path = os.path.join("Resources", "Guestbook", "Pending")
    upload_location = os.path.join(upload_path, filename)
    files = {f"{upload_location}": file_data}
    request = requests.post(url, headers=headers, files=files)

    if request.status_code == 200:
        logger.info(f"Uploaded {upload_location} to {url} successfully.")
        response.status_code = 200
        return response
    
    response.status_code = 500
    logger.error(f"Failed to post {upload_location} to {url}\nstatus code: {request.status_code}\nresponse: {request.text}")
    return response

def fetch_guestbook() -> Dict[int, 'GuestbookMessage']:
    logger.info(f"Getting list of existing guestbook entries.")
    existing_guestbook = {}
    gb = None
    request = requests.get("https://balaurbohemianbroken.neocities.org/Resources/Guestbook/guestbook.json")
    if request.status_code != 200:
        logger.error(f"Failed to get existing guestbook entries.\nStatus: {request.status_code}\nResponse:{request.text}")
        raise requests.exceptions.HTTPError
        return response
    logger.debug(f"Received guestbook data from website: {request.text}")
    try:
        existing_guestbook = request.json()
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON data from guestbook. Data: {request.text}")
        raise e
    
    # TODO: Parse into GuestbookMessage
    
    return existing_guestbook

def get_update_id() -> int:
    file_path = "data/guestbook_id.txt"
    with open(file_path, "r+") as f:
        gb_id = int(f.read())
        logger.debug(f"Fetched ID {gb_id} from {file_path}")
        f.seek(0)
        new_id = gb_id + 1
        f.write(str(new_id))
        logger.debug(f"Wrote ID {new_id} to {file_path}")
    return gb_id

# TODO: Change this into validation, separate out parsing.
def parse_guestbook_request(request):
    # TODO: Store IP in database until end of day, don't allow repeats.
    ip = request.META["REMOTE_ADDR"]
    # if ip in database

    re_chars_allowed = r"^[ -~]+$"  # all rendering ascii characters
    
    alias_size_min = 1
    alias_size_max = 32
    website_size = 128
    message_size_min = 1
    message_size_max = 512
    image_size = 0  # TODO: replace with file size
    loc_x_range = (1920 - GuestbookMessage.collision_distance) / 2
    loc_y_range = (1080 - GuestbookMessage.collision_distance) / 2
    timestamp = time()

    gb_entry = GuestbookMessage()

    data = get_json_body(request)
    # if not request.POST:
    #     logger.warning(f"Refused guestbook request: Request has no POST data.")
    #     raise BadRequest

    if not verify_input_field(data, "alias", alias_size_min, alias_size_max, re_chars_allowed):
        raise BadRequest

    gb_entry.alias = data["alias"]

    # Optional field.
    gb_entry.website = ""
    if "website" in data:
        if not verify_input_field(data, "website", 0, website_size, re_chars_allowed):
            raise BadRequest
        gb_entry.website = data["website"]

    if not verify_input_field(data, "message", message_size_min, message_size_max, re_chars_allowed):
        raise BadRequest
    gb_entry.message = data["message"]

    # TODO: Randomized position if unfilled. Maybe client-side?
    # TODO: If randomization fails, save their message anyway so I can fix it manually.
    try:
        loc_x = int(data["x"])
        loc_y = int(data["y"])
    except ValueError:
        logger.warning(f"Refused guestbook request: Invalid x, y value: ({data['x']}, {data['y']})")
        raise BadRequest
    except KeyError:
        logger.warning(f"Refused guestbook request: No x or y field")
        raise BadRequest

    if abs(loc_x) > loc_x_range:
        logger.warning(f"Refused guestbook request: x too large: {loc_x}, limit is +-{loc_x_range}")
        raise BadRequest
    if abs(loc_y) > loc_y_range:
        logger.warning(f"Refused guestbook request: y too large: {loc_y}, limit is +-{loc_y_range}")
        raise BadRequest
    gb_entry.location = Vector2(loc_x, loc_y)

    gb_entry.timestamp = timestamp
    gb_entry.id = get_update_id()

    logging.info(f"Created GuestbookMessage: {gb_entry}")
    return gb_entry

    # TODO: Image size check

    # TODO: Get list of existing messages.
    for msg in messages:
        if message.will_collide(location):
            logger.warning(f"Refused guestbook request: Input collider ({location.x}, {location.y}) overlaps ({msg.location.x}, {msg.location.y})")
            raise BadRequest

def verify_input_field(data, field, size_min, size_max, charset):
    if field not in data:
        logger.warning(f"Refused guestbook request: Field {field} not in POST request.")
        return False

    s = len(data[field])
    if s > size_max:
        logger.warning(f"Refused guestbook request: Field {field} is larger than {size_max} ({s})")
        return False
    if s < size_min:
        logger.warning(f"Refused guestbook request: Field {field} is smaller than {size_min} ({s})")
        return False
    if not re.fullmatch(charset, data[field]):
        logger.warning(f"Refused guestbook request: Field {field} does not match charset.")
        return False
    
    return True
    
def find_unoccupied_position():
    # okay the way i'm gonna do this will scale horribly
    # but i expect to get like, 20 entries.
    # i'll insert an actual sorting tree if that comes up
    # https://www.cs.cmu.edu/~jbruce/thesis/chapters/thesis-ch03.pdf
    pass

def get_json_body(request):
    # TODO: Error catching
    data = json.loads(request.body)
    logger.debug(f"Decoded data:\n{data}")
    return data

class GuestbookMessage():
    collision_distance = 32

    def __init__(self):

        # TODO: Image and sprite
        self.alias = ""
        self.website = ""
        self.message = ""
        #self.image = None
        self.location = None
        self.timestamp = 0
        self.id = 0
        #self.sprite = None
    
    # All colliders have the same size for now.
    def will_collide(self, other: 'Vector2') -> bool:
        return (self.location - other).magnitude <= collision_distance
    
    def to_dict(self):
        return {
            "alias": self.alias,
            "website": self.website,
            "message": self.message,
            "location": self.location.to_dict(),
            "timestamp": self.timestamp,
            "id": self.id,
        }

    def __str__(self):
        return f"GuestbookMessage {{alias: {self.alias}; website: {self.website}; message: {self.message}; location: {str(self.location)}, timestamp: {self.timestamp}, id: {self.id}}}"


# i reimplment this in so many languages
class Vector2():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    @property
    def magnitude(self):
        return math.sqrt(math.exp2(self.x) + math.exp2(self.y))

    def to_dict(self):
        return {"x": self.x, "y": self.y}

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __str__(self):
        return f"Vector2 {{ x: {self.x}; y: {self.y}}}"