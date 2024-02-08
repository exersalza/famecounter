import os
import re
import json
import time
import threading
import pytesseract
import socketserver

from PIL import Image, ImageGrab
from fastapi import FastAPI

from http.server import SimpleHTTPRequestHandler

TIMEOUT = 120

if os.path.exists(rf"{os.environ.get('LOCALAPPDATA')}\Programs\Tesseract-OCR"):
    tesseract_path = rf"{os.environ.get('LOCALAPPDATA')}\Programs\Tesseract-OCR\tesseract.exe"
else:
    tesseract_path = rf"{os.environ.get('ProgramData')}\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = tesseract_path
img_path = "images/img.png"
rgx = r"(fame)(\s*)|(points)"

html_score_comp_won = "<p class=\"won\">{score}</p>"
html_score_comp_lost = "<p class=\"lost\">{score}</p>"

all_games_played = []
recent = []

tracker = {
    "all_games_played": 0,
    "recent": [],
    "next": 0,
    "current": 0,
}

hmtl_useless_fcks = """<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@500&display=swap" rel="stylesheet">
</head>
<style>
    * {
        font-family: 'Roboto', sans-serif;
        margin: 0;
        padding: 0;
    }
    
    .yup {
        color: white;
    }

    .last {
        display: flex;
        flex-direction: row;
        gap: 1rem;
    }

    .lost {
        color: red;
    }

    .won {
        color: green;
    }
    
    .score {
        margin: .5rem 0;
        color: white;
    }
</style>
<script>
    function auto_reload() {setInterval(() => {fetch("http://127.0.0.1:6969").then(response => {if (!response.ok) {return;}window.location.reload(true);}).then(e => {})}, 5000)}
</script>
<body onload="auto_reload()">
"""

hmtl_content = """
<p class="score">Fame Points {current} / {togo}</p><p class="score">Games Played: {played}</p>
<div class="last">
{last_scores}
</div>
</body>
</html>
"""


def write_log():
    with open("save.json", "w") as f:
        f.write(json.dumps(tracker))


def parse_log():
    with open("save.json", "r") as f:
        j = json.loads(f.read())
        tracker["all_games_played"] = j["all_games_played"]
        tracker["recent"] = j["recent"]
        tracker["last"] = j["last"]
        tracker["current"] = j["current"]


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
    img = Image.open(img_path)
    text: str = pytesseract.image_to_string(img)
    ret = ()

    for t in text.split():
        print(t)
        if re.match(rgx, t, re.IGNORECASE):
            should_output = True

        if isnumeric(t):
            ret += (int(t),)

    if should_output:
        print(ret)
        return ret

    return None


def hmtl_creator(num: tuple):
    if num is None:
        return

    if len(recent) >= 5:
        recent.pop(0)

    score_to_append = html_score_comp_won if not num[0] < 0 else html_score_comp_lost
    tracker["recent"].append(score_to_append.format(score=num[0]))

    yup = "\n".join(recent)
    tracker["all_games_played"] += 1

    with open("./index.html", "w") as f:
        hmtl_to_write = hmtl_content.format(current=num[1], togo=num[2], last_scores=yup, played=len(all_games_played))
        f.write(hmtl_useless_fcks + hmtl_to_write)

    write_log()
    print("started timeout")
    time.sleep(TIMEOUT)
    print("ended timeout")


def start_server():
    httpd = socketserver.TCPServer(('127.0.0.1', 6969), SimpleHTTPRequestHandler)
    print("Ya server is running on http://{}:{}".format(*httpd.server_address))

    threading.Thread(target=httpd.serve_forever).start()


def clear_index():
    with open("./index.html", "w") as f:
        f.write(hmtl_useless_fcks + "</body></html>")  # start the reload timer, so we don't have to manually do it


app = FastAPI()


@app.get("/")
async def root():
    return ""


if __name__ == '__main__':
    if not os.path.exists("./images/"):
        os.mkdir("./images/")

    try:
        parse_log()
    except Exception as _:
        pass

    clear_index()
    start_server()

    while True:
        hmtl_creator(grab_data())
        time.sleep(2)
