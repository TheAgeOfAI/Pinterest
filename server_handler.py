# server_handler.py
from http.server import SimpleHTTPRequestHandler
from metadata_helper import generate_metadata

class MetadataHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/metadata.json"):
            generate_metadata()
        return super().do_GET()
