"""HTTP handler for development server with live reload functionality."""

import os
import json
from http.server import SimpleHTTPRequestHandler


class HotReloadHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler that injects live reload script into HTML pages.
    
    This handler serves files from a specified directory and automatically
    injects a live reload script into HTML pages to enable automatic page
    refreshes during development.
    
    Attributes:
        dev_server: Reference to the DevServer instance for reload version.
        dist_dir: Directory to serve files from.
    """
    
    dev_server: 'DevServer' = None  # type: ignore
    dist_dir: str = None  # type: ignore
    reload_script_content: str = None  # type: ignore
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.dist_dir, **kwargs)
        
        # Read reload script once during initialization
        if self.reload_script_content is None:
            reload_js_path = os.path.join(os.path.dirname(__file__), 'reload_outdated.js')
            with open(reload_js_path, 'r', encoding='utf-8') as f:
                HotReloadHandler.reload_script_content = f.read()
        
    def do_GET(self):
        """Handle GET requests with reload script injection for HTML files."""
        # Handle reload check endpoint
        if self.path == '/__dev_reload_check__':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json.dumps({'version': self.dev_server.reload_version}).encode())
            return
            
        # For HTML files, inject reload script
        if self.path.endswith('.html') or self.path == '/':
            file_path = os.path.join(self.dist_dir, self.path.lstrip('/'))
            if self.path == '/':
                file_path = os.path.join(self.dist_dir, 'index.html')
                
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use cached reload script and replace version placeholder
                reload_script_content = self.reload_script_content.replace(
                    '__CURRENT_VERSION__', 
                    str(self.dev_server.reload_version)
                )
                
                reload_script = f'<script>\n{reload_script_content}\n</script>\n</body>'
                content = content.replace('</body>', reload_script)
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(content.encode())))
                self.end_headers()
                self.wfile.write(content.encode())
                return
        
        # Default behavior for other files
        super().do_GET()
