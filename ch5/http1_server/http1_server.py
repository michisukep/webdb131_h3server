from http.server import BaseHTTPRequestHandler, HTTPServer
from argparse import ArgumentParser
import ssl


class MyReqHandler(BaseHTTPRequestHandler):
  port = None

  def do_GET(self):
    self.send_response(200)
    self.send_header('Content-Type', 'text/html')
    self.send_header('Alt-Svc',
            f'h3=":{MyReqHandler.port}"; ma=3600')
    self.end_headers()

    content = \
        b"<html><body>Test Http Server</body></html>"
    self.wfile.write(content)

  def do_POST(self):
    self.do_GET()

if __name__ == '__main__':
  p = ArgumentParser()
  p.add_argument("--host", type=str,
                 default="0.0.0.0")
  p.add_argument("--port", type=int, default=8443)
  p.add_argument("--cert", type=str)
  p.add_argument("--key", type=str)

  args = p.parse_args()
  MyReqHandler.port = args.port

  ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
  ctx.load_cert_chain(args.cert, args.key)

  s = HTTPServer((args.host, args.port), MyReqHandler)
  s.socket = ctx.wrap_socket(s.socket, server_side=True)

  print(f"Starting Http Server: {args.host}:{args.port}")
  s.serve_forever()
