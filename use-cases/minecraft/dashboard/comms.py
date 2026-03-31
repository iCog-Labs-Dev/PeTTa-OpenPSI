import json
import os
import socket
from typing import Any

HOST = os.getenv("OPENPSI_DASHBOARD_HOST", "127.0.0.1")
PORT = int(os.getenv("OPENPSI_DASHBOARD_PORT", "5001"))
_client: socket.socket | None = None
_last_endpoint_printed: tuple[str, int] | None = None


def set_endpoint(host: str, port: int | None = None) -> None:
    global HOST, PORT, _client
    # Accept either (host, port) or a single sequence like [host, port].
    if port is None:
        if isinstance(host, (list, tuple)) and len(host) >= 2:
            host, port = host[0], host[1]
        else:
            raise TypeError("set_endpoint requires host and port")

    HOST = str(host)
    PORT = int(port)
    if _client is not None:
        try:
            _client.close()
        except OSError:
            pass
        _client = None


def _get_client() -> socket.socket:
    global _client
    if _client is None:
        _client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _client.connect((HOST, PORT))
    return _client


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    return str(value)


def send_event(event):
    global _client, _last_endpoint_printed
    safe_event = _json_safe(event)
    message = json.dumps(safe_event) + "\n"
    data = message.encode("utf-8")

    # Reconnect once if the peer restarted.
    try:
        client = _get_client()
        client.sendall(data)
    except OSError:
        if _client is not None:
            try:
                _client.close()
            except OSError:
                pass
            _client = None
        client = _get_client()
        client.sendall(data)

    endpoint = (HOST, PORT)
    if _last_endpoint_printed != endpoint:
        print(f"[dashboard] sending events to {HOST}:{PORT}")
        _last_endpoint_printed = endpoint