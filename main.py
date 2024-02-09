import os
import re
import json
import time
import threading

import pytesseract
import uvicorn

from PIL import Image, ImageGrab
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

TIMEOUT = 120

if os.path.exists(rf"{os.environ.get('LOCALAPPDATA')}\Programs\Tesseract-OCR"):
    tesseract_path = rf"{os.environ.get('LOCALAPPDATA')}\Programs\Tesseract-OCR\tesseract.exe"
else:
    tesseract_path = rf"{os.environ.get('ProgramData')}\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = tesseract_path
img_path = "images/img.png"
rgx = r"(fame)(\s*)|(points)"  # capture "famepoints" and "fame points", weird ocr stuff
capture_section = (849, 787, 1145, 1007)

app = FastAPI()

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
        for k, v in json.loads(f.read()).items():
            tracker[k] = v


def isnumeric(text: str) -> bool:
    """ IT IS JUST NEGATIVE OK

    :param text: da text
    :return: a bool
    """
    return text.removeprefix("-").isnumeric()


def make_screen():
    try:  # fuck around find out here because can't screenshot in uac windows for ex.
        ImageGrab.grab(bbox=capture_section).save(img_path)
    except Exception as e:
        print(e)  # just show an error message, don't kill the program not good


def match_img():
    make_screen()
    img = Image.open(img_path)
    text: str = pytesseract.image_to_string(img).split()

    if not len(text) > 0:
        return None

    if not re.match(rgx, text[0], re.IGNORECASE):  # 99.99e9999 of cases the first one was famepoints or fame points
        return None

    return text


# ret = ()

def grab_data():
    # global ret  # we do not care
    try:
        ImageGrab.grab(bbox=(849, 787, 1145, 1007)).save(img_path)
    except Exception as e:
        print(e)
        return None

    should_output = match_img()
    persistent_ret = ()

    if not should_output:
        return None

    while True:
        text = match_img()
        ret = ()  # why tf does python not have a clear function, i want to go back to rust

        if not text:
            ret = persistent_ret
            break

        for t in text:
            if isnumeric(t):
                ret += (int(t),)

        persistent_ret = ret
        time.sleep(.5)

    if len(ret) == 3:  # wanna insert something when shits done
        tracker["all_games_played"] += 1

        if len(tracker["recent"]) >= 5:
            tracker["recent"].pop(0)

        tracker["recent"].append(ret[0])
        tracker["current"] = ret[1]
        tracker["next"] = ret[2]
        tracker["all"] += int(ret[0])
        write_log()


@app.get("/update")
async def get_update():
    return tracker


# has to be last, otherwise brokie
app.mount("/", StaticFiles(directory="_internal/dist/"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_server():
    print(f"{'*'*50}\n\nPaste this in OBS: http://127.0.0.1:6969/index.html\n\n{'*'*50}")
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
