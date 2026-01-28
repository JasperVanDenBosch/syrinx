"""HTTP handler for development server with live reload functionality."""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import os
import json
from http.server import SimpleHTTPRequestHandler
if TYPE_CHECKING:
    from syrinx.server.dev_server import DevServer


class HotReloadHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler that injects live reload script into HTML pages.
    
    This handler serves files from a specified directory and automatically
    injects a live reload script into HTML pages to enable automatic page
    refreshes during development.
    
    Attributes:
        dev_server: Reference to the DevServer instance for reload version.
        dist_dir: Directory to serve files from.
        reload_script_content: JavaScript content for live reload functionality.
    """
    
    dev_server: DevServer
    dist_dir: str
    reload_script_content: str
    
    @classmethod
    def initialize(cls, dev_server: DevServer, dist_dir: str):
        """Initialize class-level properties before server starts.
        
        This method must be called before the TCPServer starts accepting
        requests to ensure all class properties are properly initialized.
        
        Args:
            dev_server: Reference to the DevServer instance.
            dist_dir: Directory to serve files from.
        """
        cls.dev_server = dev_server
        cls.dist_dir = dist_dir
        
        # Load reload script once during class initialization
        reload_js_path = os.path.join(os.path.dirname(__file__), 'reload_outdated.js')
        with open(reload_js_path, 'r', encoding='utf-8') as f:
            cls.reload_script_content = f.read()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.dist_dir, **kwargs)
        
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
