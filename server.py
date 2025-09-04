# serve.py
import time
import os
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from metadata_helper import generate_metadata
from server_handler import MetadataHandler

PORT = 8000
IMAGE_DIR = "images"

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def watch_images(interval=5):
    """Watch for new/removed images and regenerate metadata.json"""
    prev = set(os.listdir(IMAGE_DIR)) if os.path.exists(IMAGE_DIR) else set()
    while True:
        time.sleep(interval)
        if not os.path.exists(IMAGE_DIR):
            continue
        now = set(os.listdir(IMAGE_DIR))
        if now != prev:
            generate_metadata()
            prev = now

if __name__ == "__main__":
    # Initial metadata
    generate_metadata()

    # Start watcher in background
    import threading
    threading.Thread(target=watch_images, daemon=True).start()

    # Start server
    server_address = ("", PORT)
    httpd = ThreadingSimpleServer(server_address, MetadataHandler)
    print(f"🌐 Serving on http://localhost:{PORT}")
    httpd.serve_forever()
