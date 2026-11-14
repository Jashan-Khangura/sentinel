import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from nanobot.gateway.runtime import (
    _gateway_health_ready,
)


@pytest.fixture
def health_server():
    reply = {"status": 200, "body": b'{"status":"ok"}'}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            assert self.path == "/health"
            self.send_response(reply["status"])
            self.end_headers()
            self.wfile.write(reply["body"])

        def log_message(self, *_args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1], reply
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


def test_health_probe_accepts_a_ready_gateway(health_server):
    port, reply = health_server
    reply["body"] = json.dumps({"status": "ok", "ready": True}).encode()
    assert _gateway_health_ready("127.0.0.1", port)


@pytest.mark.parametrize("status,body", [
    (503, b'{"status":"ok","ready":true}'),
    (200, b'{"status":"ok","ready":false}'),
    (200, b'{"status":"ok"}' + b' ' * 4096),
    (200, b'[]'),
])
def test_unready_or_invalid_response_is_not_ready(health_server, status, body):
    port, reply = health_server
    reply.update(status=status, body=body)
    assert not _gateway_health_ready("127.0.0.1", port)
