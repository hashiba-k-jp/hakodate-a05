from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs


class RequestHandler(BaseHTTPRequestHandler):

    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)

    def do_POST(self):
        self.send_response(200)
        self.send_header("User-Agent","test1")
        self.end_headers()
        html = "abcd"
        self.wfile.write(html.encode())

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        content_len  = int(self.headers.get("content-length"))
        req_body = self.rfile.read(content_len).decode("utf-8")
        body  = "method: " + str(self.command) + "\n"
        body += "params: " + str(params) + "\n"
        body += "body  : " + req_body + "\n"
        print(req_body)
        print(type(req_body))
        # run any programs here ?

    def do_GET(self):
        self.send_response(200)
        self.send_header("User-Agent","test1")
        self.end_headers()
        html = "abc"
        self.wfile.write(html.encode())


ip = 'localhost'
port = 8000
server = HTTPServer((ip, port), RequestHandler)
server.serve_forever()
