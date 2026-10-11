from flask import Flask, jsonify, request 
import requests
from io import BytesIO
from PIL import Image, ImageOps
from websockets.sync.client import connect

app = Flask(__name__) 

methods = {"am": requests.get, "ar": requests.post, "az": requests.put, "eu": requests.delete, "bg": requests.patch, "ca": requests.options}
body_methods = (requests.post, requests.put, requests.patch)
types = {"text/html": "h", "text/css": "c", "text/plain": "t", "image/avif": "i", "image/bmp": "i", "image/gif": "i", "image/jpeg": "i", "image/png": "i", "image/tiff": "i", "application/json": "j"}

color_to_b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
def process_image(_image: bytes):
    image = Image.open(BytesIO(_image))
    image = image.convert("RGB")

    if image.width > 256 or image.height > 256:
        image = ImageOps.contain(image, (256, 256))

    palette = Image.open("palette.png")
    image = image.quantize(palette=palette)

    string = ""
    for j in range(image.height):
        for i in range(image.width):
            pixel = image.getpixel((i, j))
            char = color_to_b64[pixel]
            string += char
        string += "="

    return string

@app.route('/translate', methods=['GET']) 
def server(): 
    full_txt = request.args["text"].split("|")

    match txt.split(":")[0]: # Scheme of URI
        case "http" | "https":
            txt = full_txt[0]
            body = full_txt[1]
            method = methods[request.args["language"]]
            if method in body_methods: 
                result = method(txt, body)

                filetype = types.get(result.headers["content-type"].split(";")[0], "d")

                data = {"result": "|".join((str(result.status_code), filetype, result.text))}
            else: 
                result = method(txt)

                if request.args["language"] == "ca":
                    filetype = "n"
                    header = "allow"
                else:
                    filetype = types.get(result.headers["content-type"].split(";")[0], "d")
                match filetype:
                    case "h" | "c" | "t" | "j":
                        text = result.text
                    case "i":
                        text = process_image(result.content)
                    case "d":
                        text = result.content.hex()
                    case "n":
                        text = result.headers[header]
                data = {"result": "|".join((str(result.status_code), filetype, text))}
        case "ws" | "wss":
            txt = full_txt[0]
            body = full_txt[1]
            with connect(txt) as socket:
                socket.send(body)
                data = {"result": f"{socket.recv()}"}
        case _:
            data = {"result": "ERROR! That protocol is not supported. Supported protocols: HTTP, WebSocket"}

    print(data)
    res = jsonify(data)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res
    
if __name__ == '__main__': 
    app.run(host='127.0.0.1', port=443, ssl_context=("server.crt", "server.key"))
