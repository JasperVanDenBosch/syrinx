"""Development server module for Syrinx with file watching and live reload.

This module provides a development server that watches for file changes in the
parent directory hierarchy and automatically rebuilds the site when changes are
detected. It includes an HTTP server to serve the built files.
"""

import os
from socketserver import TCPServer
from watchdog.observers import Observer
from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from syrinx.server.hot_reload_handler import HotReloadHandler
from syrinx.server.rebuild_handler import RebuildHandler


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
        
        # Configure the handler class attributes
        HotReloadHandler.dev_server = self
        HotReloadHandler.dist_dir = dist_dir
        
        try:
            with TCPServer(("", self.port), HotReloadHandler) as httpd:
                print(f"\n[DEV] Server running at http://localhost:{self.port}")
                print("[DEV] Press Ctrl+C to stop\n")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[DEV] Shutting down...")
            observer.stop()
        finally:
            observer.join()
            os.chdir(original_dir)
