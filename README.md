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
                 Leave empty
                 if not used
                (Keep the |)
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
status|filetype|body <- Body
  ^^      ^^<< Filetype
Status code    h = Html
               c = Css
               t = plainText
               i = Image (base64 encoded)
               d = Data (lowercase hex encoded)
               n = http (Network) header
               j = Json
               x = Xml
```

# Usage (WebSocket)

- Translate text in the following format:

```
wss://example.com|data
       ^^          ^^
       URL        Data to send
```

- Language is irrelevant.
- The response will be in this format:

```
response
   ^^
Server response
```
