based on code from https://activation.nreal.ai/en/nreal-air-upgrade-plus.html

i run it locally by using https://www.npmjs.com/package/http-server

`npm i -g http-server`

make sure you generate a cert using `127.0.0.1` as the **Common** name

`openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem`

`http-server -S -C cert.pem`

if you're using chrome you may need to type `thisisunsafe` to bypass the invalid cert warning
or, just add the cert to your computer's certificate keychain

(ssl/https is required for the WebUSB HID connections)

using this as a framework for exploring the Nreal Air usb protocol
combined with Wireshark for USB packet-sniffing

See [findings.md](findings.md) for more info
