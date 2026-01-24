"""Development server module for Syrinx with file watching and live reload.

This module provides a development server that watches for file changes in the
parent directory hierarchy and automatically rebuilds the site when changes are
detected. It includes an HTTP server to serve the built files.
"""

import os
import time
from pathlib import Path
import http.server
import socketserver
import threading
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess


class RebuildHandler(FileSystemEventHandler):
    """File system event handler that triggers rebuilds on file changes.
    
    This handler watches for file system events and triggers a rebuild of the
    Syrinx site when relevant files are modified. It includes debouncing to
    avoid excessive rebuilds and filters out irrelevant changes.
    
    Attributes:
        root_dir: The root directory of the Syrinx project to build.
        watch_dir: The parent directory to watch for changes.
        last_build_time: Timestamp of the last build to implement debouncing.
        build_delay: Minimum delay between builds in seconds.
        reload_callback: Callback function to trigger browser reload.
    """
    def __init__(self, root_dir, watch_dir, reload_callback=None):
        self.root_dir = root_dir
        self.watch_dir = watch_dir
        self.last_build_time = 0
        self.build_delay = 0.5  # seconds
        self.reload_callback = reload_callback
        
    def on_any_event(self, event):
        """Handle any file system event by rebuilding if necessary.
        
        Args:
            event: A watchdog FileSystemEvent object containing information
                about the file system change.
        """
        if event.is_directory:
            return
            
        # Ignore dist directory changes to avoid infinite loops
        if 'dist' in event.src_path:
            return
            
        # Ignore hidden files and common editor temp files
        if any(part.startswith('.') for part in Path(event.src_path).parts):
            return
            
        # Ignore Python cache files
        if '__pycache__' in event.src_path or event.src_path.endswith('.pyc'):
            return
            
        current_time = time.time()
        if current_time - self.last_build_time > self.build_delay:
            self.last_build_time = current_time
            print(f"\n[DEV] File changed: {event.src_path}")
            self.rebuild()
    
    def rebuild(self):
        """Rebuild the Syrinx site.
        
        Runs the full build pipeline including preprocessing, reading,
        and building. Catches and prints any errors that occur during
        the build process.
        """
        try:
            print("[DEV] Rebuilding...")
            preprocess(self.root_dir, clean=False)
            root = read(self.root_dir)
            build(root, self.root_dir)
            print("[DEV] Build complete!")
            
            # Trigger browser reload if callback is set
            if self.reload_callback:
                self.reload_callback()
        except Exception as e:
            print(f"[DEV] Build error: {e}")


class DevServer:
    """Development server with file watching and HTTP serving.
    
    Provides a complete development environment for Syrinx projects by:
    - Watching parent directories for file changes
    - Automatically rebuilding on changes
    - Serving the built files via HTTP
    
    Attributes:
        root_dir: The absolute path to the Syrinx project root.
        port: The port number for the HTTP server.
        reload_version: Version counter for triggering reloads.
    """
    def __init__(self, root_dir, port=8000):
        self.root_dir = os.path.abspath(root_dir)
        self.port = port
        self.reload_version = 0
        
    def trigger_reload(self):
        """Increment reload version to trigger browser reloads."""
        self.reload_version += 1
        
    def start(self):
        """Start the development server.
        
        Performs an initial build, sets up file watching on the parent
        directory, and starts an HTTP server to serve the dist directory.
        The server runs until interrupted with Ctrl+C.
        """
        # Determine parent directory to watch
        watch_dir = os.path.dirname(self.root_dir)
        print(f"[DEV] Watching for changes in: {watch_dir}")
        print(f"[DEV] Building from: {self.root_dir}")
        
        # Initial build
        print("[DEV] Initial build...")
        preprocess(self.root_dir, clean=False)
        root = read(self.root_dir)
        build(root, self.root_dir)
        print("[DEV] Initial build complete!")
        
        # Setup file watcher with reload callback
        event_handler = RebuildHandler(self.root_dir, watch_dir, self.trigger_reload)
        observer = Observer()
        observer.schedule(event_handler, watch_dir, recursive=True)
        observer.start()
        
        # Setup HTTP server
        dist_dir = os.path.join(self.root_dir, 'dist')
        
        # Store original directory to restore later
        original_dir = os.getcwd()
        
        # Create a custom handler that serves from dist_dir and injects reload script
        dev_server = self
        
        class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=dist_dir, **kwargs)
                
            def do_GET(self):
                # Handle reload check endpoint
                if self.path == '/__dev_reload_check__':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    self.wfile.write(json.dumps({'version': dev_server.reload_version}).encode())
                    return
                    
                # For HTML files, inject reload script
                if self.path.endswith('.html') or self.path == '/':
                    file_path = os.path.join(dist_dir, self.path.lstrip('/'))
                    if self.path == '/':
                        file_path = os.path.join(dist_dir, 'index.html')
                        
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Inject reload script before </body>
                        reload_script = f'''
<script>
(function() {{
    let currentVersion = {dev_server.reload_version};
    setInterval(async () => {{
        try {{
            const response = await fetch('/__dev_reload_check__');
            const data = await response.json();
            if (data.version !== currentVersion) {{
                console.log('[DEV] Reloading page...');
                window.location.reload();
            }}
        }} catch (e) {{
            console.error('[DEV] Reload check failed:', e);
        }}
    }}, 1000);
}})();
</script>
</body>'''
                        content = content.replace('</body>', reload_script)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.send_header('Content-Length', str(len(content.encode())))
                        self.end_headers()
                        self.wfile.write(content.encode())
                        return
                
                # Default behavior for other files
                super().do_GET()
        
        try:
            with socketserver.TCPServer(("", self.port), CustomHTTPHandler) as httpd:
                print(f"\n[DEV] Server running at http://localhost:{self.port}")
                print("[DEV] Press Ctrl+C to stop\n")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[DEV] Shutting down...")
            observer.stop()
        finally:
            observer.join()
            os.chdir(original_dir)