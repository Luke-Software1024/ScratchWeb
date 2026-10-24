# ScratchWeb
Web requests in vanilla Scratch 3.0

# Setup

- Create a certificate. Name it `server.crt` with the key file named `server.key`.
- Install the `requirements.txt` dependencies
- Simply add `127.0.0.1 translate-service.scratch.mit.edu` to your hosts file (on windows - ~~untested on linux~~ Linux works too - untested on macOS)
- Run `server.py`
- Add a security exception for `translate-service.scratch.mit.edu` in your browser; the certificate is self-signed, and therefore, insecure

# How it works

<img width="1920" height="1032" alt="translate" src="https://github.com/user-attachments/assets/781a1d32-397f-4132-9781-8868d796ce4c" />

When the translate feature is used in Scratch, It sends an HTTP `GET` request to `translate-service.scratch.mit.edu`.
<img width="1920" height="299" alt="inspect" src="https://github.com/user-attachments/assets/bb1b271d-b414-4247-9393-7b63ea776f58" />

Route the `translate-service.scratch.mit.edu` to localhost in the Hosts File.
<img width="666" height="746" alt="hosts-file" src="https://github.com/user-attachments/assets/a7a80540-5406-424f-9731-ffaccf2633d9" />

Create a custom script to interpret the text and language to make a web request.
<img width="1560" height="943" alt="script" src="https://github.com/user-attachments/assets/1d3f40d1-49b0-486e-9348-dfac99d154ea" />

# Usage (HTTP)

- Import the `translate` extension to the project.
- Translate text in the following format:

```
https://example.com|body
        ^^          ^^
        URL        Body
               If applicable;
               Don't include
               if not used
```

- To one of these languages:

|Language|Method|Uses Body?|
|---|---|---|
|Amharic|GET|No|
|Arabic|POST|Yes|
|Azerbaijani|PUT|Yes|
|Basque|DELETE|No|
|Bulgarian|PATCH|Yes|
|Catalan|OPTIONS|No|

- The response will be in this format:

```
status|filetype|body
  ^^      ^^     ^^
Status Filetype  Body
 code  h = Html (text/html)
       c = Css (text/css)
       t = plainText (text/plain)
       i = Image (base64 encoded) (image/*)
       d = Data (lowercase hex encoded) (*/*)
       n = Network header (application/http)
       j = Json (application/json)
       x = Xml (*/xml)
```

# Usage (WebSocket)

- Translate text in the following format:

```
wss://example.com|data
       ^^          ^^
       URL    Data to send
```

- The response will be in this format:

```
response
   ^^
Server response
```

# Usage (`data:` URI)

- Please note that only base64 encoded data is supported.
- Translate text in the following format:

```
data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==
                   ^^
               data: URI
```

- The response will be in this format:

```
filetype|data
   ^^     ^^
Filetype; Data
Mapping
same as
  HTTP
```
# ScratchWeb Outsource

ScratchWeb Outsource allows you to 'outsource' tasks to the ScratchWeb server.

## Setup

The file `outsrc.py` must:

- Contain a dictionary named `funcs` mapping function names to function objects.
- Contain one or more functions that expect 2 string arguments and return a string.

An example is included.

## Usage

- Translate text in the following format:

```
outsrc:function-name|argument
            ^^          ^^
       Function name Argument
       Indexed into  Passed to
       funcs dict    function
       and called
```

- To a language determined by the script.
- The response will be in this format:

```
data
 ^^
Returned data
```

# Usage (`file:` URI)

- Only the `file` subfolder of ScratchWeb is accessible.
- Translate text in the following format:

```
file:///example.txt
         ^^
      file: URI
```

- The response will be in one of these formats:
- Directory:

```
l|example.txt|16|2147483647 folder|0|2147483647
      ^^      ^^     ^^             ^^
   Filename Size Date modded     Next item
                 (Unix time)
```

- File:

```
d|44617461
     ^^
  File contents
  Hex encoded (lowercase letters)
```