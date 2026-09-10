"""HTTP transport for explicit per-request generation limits.

Kept separate from the historical fixed-budget benchmark transport.
"""
import json
import queue
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def make_server(scheduler, host='127.0.0.1', port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def reply(self, code, body):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.reply(200 if self.path == '/health' else 404,
                       {'status': 'ok'} if self.path == '/health' else {'error': 'not found'})

        def do_POST(self):
            try:
                self.connection.settimeout(30)
                length = int(self.headers.get('Content-Length', '0'))
                if not 1 <= length <= 65536 or self.headers.get('Transfer-Encoding'):
                    raise ValueError('bounded Content-Length required')
                body = json.loads(self.rfile.read(length))
                request_id = body.get('request_id')
                if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
                    raise ValueError('bounded request_id required')
                if self.path == '/cancel':
                    self.reply(200, {'cancelled': scheduler.cancel(request_id)})
                    return
                if self.path != '/stream':
                    self.reply(404, {'error': 'not found'})
                    return
                prompt = body.get('prompt')
                if not isinstance(prompt, str) or not 1 <= len(prompt) <= 4096:
                    raise ValueError('bounded nonempty prompt required')
                limit = body.get('max_new_tokens', scheduler.max_tokens)
                if limit is None:
                    raise ValueError('max_new_tokens cannot be null')
                request = scheduler.submit(request_id, prompt, limit)
            except queue.Full:
                self.reply(429, {'error': 'queue full'})
                return
            except (ValueError, TypeError, AttributeError) as exc:
                self.reply(400, {'error': str(exc)})
                return
            except RuntimeError as exc:
                self.reply(503, {'error': str(exc)})
                return
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-ndjson')
                self.end_headers()
                while True:
                    event = request.events.get(timeout=60)
                    self.wfile.write((json.dumps(event) + '\n').encode())
                    self.wfile.flush()
                    if event['type'] == 'done':
                        break
            except (OSError, queue.Empty):
                scheduler.cancel(request_id)
            finally:
                scheduler.cancel(request_id)
    class Server(ThreadingHTTPServer):
        request_queue_size = 128
    return Server((host, port), Handler)
