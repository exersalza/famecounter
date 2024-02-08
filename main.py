import os
import re
import json
import time
import threading

import pytesseract
import socketserver
import uvicorn

from PIL import Image, ImageGrab
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from http.server import SimpleHTTPRequestHandler

TIMEOUT = 120

if os.path.exists(rf"{os.environ.get('LOCALAPPDATA')}\Programs\Tesseract-OCR"):
    tesseract_path = rf"{os.environ.get('LOCALAPPDATA')}\Programs\Tesseract-OCR\tesseract.exe"
else:
    tesseract_path = rf"{os.environ.get('ProgramData')}\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = tesseract_path
img_path = "images/img.png"
rgx = r"(fame)(\s*)|(points)"

app = FastAPI()

tmp = []

tracker = {
    "all_games_played": 0,
    "recent": [],
    "next": 0,
    "current": 0,
    "all": 0  # all gained and lost fp added
}


def write_log():
    with open("save.json", "w") as f:
        f.write(json.dumps(tracker))


def parse_log():
    with open("save.json", "r") as f:
        j = json.loads(f.read())
        tracker["all_games_played"] = j["all_games_played"]
        tracker["recent"] = j["recent"]
        tracker["next"] = j["next"]
        tracker["current"] = j["current"]
        tracker["all"] = j["all"]


def isnumeric(text: str) -> bool:
    """ IT IS JUST NEGATIVE OK

    :param text: da text
    :return: a bool
    """
    return text.removeprefix("-").isnumeric()


def grab_data():
    try:
        ImageGrab.grab(bbox=(849, 787, 1145, 1007)).save(img_path)
    except Exception as e:
        print(e)
        return None

    should_output = False
    should_should_output = False
    img = Image.open(img_path)
    text: str = pytesseract.image_to_string(img)
    ret = ()

    for t in text.split():
        if re.match(rgx, t, re.IGNORECASE):
            should_output = True

        if isnumeric(t):
            ret += (int(t),)

    if should_output:
        tmp.append(ret[0])
        tmp.sort()

        tracker["all_games_played"] += 1
        tracker["recent"].append(ret[0])
        tracker["current"] = tmp[-1]
        tracker["next"] = ret[2]
        tracker["all"] += int(ret[0])



@app.get("/update")
async def get_update():
    return tracker


# has to be last, otherwise brokie
app.mount("/", StaticFiles(directory="dist/"), name="static")


def start_server():
    uvicorn.run(app, host="127.0.0.1", port=6969)


def start_grabber():
    while True:
        grab_data()
        time.sleep(1)


if __name__ == '__main__':
    if not os.path.exists("./images/"):
        os.mkdir("./images/")

    if os.path.exists("./save.json"):
        parse_log()

    threading.Thread(target=start_grabber).start()

    start_server()
