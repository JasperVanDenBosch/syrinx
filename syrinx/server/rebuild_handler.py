"""File system event handler for automatic rebuilds."""

import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from syrinx.run import run_pipeline


class RebuildHandler(FileSystemEventHandler):
    """File system event handler that triggers rebuilds on file changes.
    
    This handler watches for file system events and triggers a rebuild of the
    Syrinx site when relevant files are modified. It includes debouncing to
    avoid excessive rebuilds and filters out irrelevant changes.
    
    Attributes:
        root_dir: The root directory of the Syrinx project to build.
        watch_dir: The parent directory to watch for changes.
        args: Command-line arguments for configuration.
        last_build_time: Timestamp of the last build to implement debouncing.
        build_delay: Minimum delay between builds in seconds.
        reload_callback: Callback function to trigger browser reload.
    """
    def __init__(self, root_dir, watch_dir, reload_callback, args):
        self.root_dir = root_dir
        self.watch_dir = watch_dir
        self.args = args
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
            run_pipeline(self.args)
            print("[DEV] Build complete!")
            
            # Trigger browser reload if callback is set
            if self.reload_callback:
                self.reload_callback()
        except Exception as e:
            print(f"[DEV] Build error: {e}")
