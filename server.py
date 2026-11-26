from flask import Flask, jsonify, request 
import requests
from io import BytesIO
from PIL import Image, ImageOps
from websockets.sync.client import connect
from base64 import b64decode
import outsrc
from pathlib import Path

app = Flask(__name__) 

http_methods = {"am": requests.get, "ar": requests.post, "az": requests.put, "eu": requests.delete, "bg": requests.patch, "ca": requests.options}
http_body_methods = (requests.post, requests.put, requests.patch)
types = {"text/html": "h", "text/css": "c", "text/plain": "t", "image/avif": "i", "image/bmp": "i", "image/gif": "i", "image/jpeg": "i", "image/png": "i", "image/tiff": "i", "application/json": "j", "application/xml": "x", "text/xml": "x"}

# Convert images to custom b64 format
color_to_b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
def process_image(_image: bytes):
    # Open it
    image = Image.open(BytesIO(_image))
    image = image.convert("RGB")

    # Scale to Scratch-appropriate resolution
    if image.width > 480 or image.height > 360:
        image = ImageOps.contain(image, (480, 360))

    # Map to 6-bit RGB palette
    # palette.png may look empty, but it has an indexed palette that is used
    # here to quantize to the palette.
    palette = Image.open("palette.png")
    image = image.quantize(palette=palette)

    # Convert image to b64 characters
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
    # Get some info
    full_txt = request.args["text"].split("|")
    txt = full_txt[0]
    command = request.args["language"]

    # Do the thing
    match txt.split(":")[0]: # Scheme of URI
        case "http" | "https":
            # Make a HTTP request
            method = http_methods[command]
            if method in http_body_methods: # this method can have a request body
                filetype = full_txt[1]
                body = "|".join(full_txt[2:])

                if filetype == "d":
                    body = bytes.fromhex(body)

                result = method(txt, body)

                filetype = types.get(result.headers["content-type"].split(";")[0], "d")

                data = {"result": "|".join((str(result.status_code), filetype, result.text))}
            else: 
                result = method(txt)

                # special case: OPTIONS method returns the value of a header
                if request.args["language"] == "ca":
                    filetype = "n"
                    header = "allow"
                else:
                    filetype = types.get(result.headers["content-type"].split(";")[0], "d")
                match filetype:
                    case "h" | "c" | "t" | "j" | "x":
                        text = result.text
                    case "i":
                        text = process_image(result.content)
                    case "d":
                        text = result.content.hex()
                    case "n":
                        text = result.headers[header]
                data = {"result": "|".join((str(result.status_code), filetype, text))}
        
        case "ws" | "wss":
            # Send data over WebSocket and get the response
            body = "|".join(full_txt[1:])
            with connect(txt) as socket:
                socket.send(body)
                data = {"result": f"{socket.recv()}"}
        
        case "data":
            # Decode a data URI
            # WARNING - Only works on base64 encoded data!
            mimetype = txt.split(":")[1].split(";")[0]
            filetype = types.get(mimetype, "d")
            data = b64decode(txt.split(",")[1], "-_") # use base64-URL encoding
            match filetype:
                case "h" | "c" | "t" | "j" | "x":
                    text = data.decode()
                case "i":
                    text = process_image(data)
                case "d":
                    text = data.hex()
            data = {"result": "|".join((filetype, text))}
        
        case "outsrc":
            # Run a script through ScratchWeb Outsource
            func = txt.split(":")[1]
            arg = "|".join(full_txt[1:])

            # If that function exists and outsrc: URI is allowed for it, get
            # it. Otherwise, get a placeholder that returns an error message
            if outsrc.funcs.get(func, (0, 0))[1] != 1:
                func = outsrc.funcs.get(func, (lambda a, b: "ERROR! That Outsource function does not exist. Existent functions: " + ", ".join(outsrc.funcs.keys()), 0))[0]
                result = func(arg, command)
                data = {"result": result}
            else:
                data = {"result": "ERROR! That Outsource function is not allowed to be invoked by outsrc: URI."}

        case "file":
            # Get a file/directory from the file subfolder
            folder = Path("file") / txt.removeprefix("file:///")

            if folder.is_dir(): # Get a directory listing
                contents = folder.iterdir()
                format_conts = []
                for item in contents:
                    info = item.stat()
                    format_conts.append("|".join((str(item).split("/")[-1], str(info.st_size), str(info.st_mtime))))
                data = {"result": "l|" + " ".join(format_conts)}
            elif folder.is_file(): # Get the file
                contents = folder.read_bytes()
                data = {"result": "d|" + contents.hex()}
            else: # Nonexistent file!
                data = {"result": "ERROR! That file does not exist."}

        case _:
            if txt.split(":")[0] in outsrc.alt_ids:
                # Outsource script with raw-URI format
                func = txt.split(":")[0]
                arg = ":".join(txt.split(":")[1:])

                func = outsrc.funcs[outsrc.alt_ids[func]][0]
                result = func(arg, command)
                data = {"result": result}
            elif txt.split(":")[0] in outsrc.funcs:
                # Raw-URI not allowed!
                data = {"result": "ERROR! That Outsource function is not allowed to be invoked by Raw-URI."}
            else:
                # Unknown protocol!
                data = {"result": "ERROR! That protocol is not supported. Supported protocols: HTTP, WebSocket; Supported URIs: data, outsrc, file"}

    print(data)
    res = jsonify(data)
    res.headers.add('Access-Control-Allow-Origin', '*') # CORS compliance
    return res
    
if __name__ == '__main__': 
    app.run(host='127.0.0.1', port=443, ssl_context=("server.crt", "server.key"))
