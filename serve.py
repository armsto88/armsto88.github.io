"""Simple HTTP server with correct MIME types for .glb files."""
import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.glb': 'model/gltf-binary',
    '.gltf': 'model/gltf+json',
})

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()