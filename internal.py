#!/usr/bin/env python3

import os, ssl, json
from OpenSSL import crypto
from http.server import BaseHTTPRequestHandler, HTTPServer

CERTFILE = "./server.pem"


class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=UTF-8")
        self.end_headers()
        msg = {"msg": "Hello!", "path": self.path}
        self.wfile.write(bytes(json.dumps(msg), "utf-8"))


def cert_gen(certFile, commonName="127.0.0.1", serialNumber=0, validityStartInSeconds=0, validityEndInSeconds=10 * 365 * 24 * 60 * 60):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    cert = crypto.X509()
    cert.get_subject().CN = commonName
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(validityStartInSeconds)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha512")
    with open(certFile, "w") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))


if __name__ == "__main__":
    if not os.path.exists(CERTFILE):
        cert_gen(CERTFILE)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTFILE)
    httpd = HTTPServer(("127.0.0.1", 8443), HelloHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    try:
        httpd.serve_forever()
    finally:
        httpd.socket.close()
