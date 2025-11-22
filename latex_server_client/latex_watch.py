
#!/usr/bin/env python3
"""
LaTeX Watch - Automatic compilation on file changes

A command-line tool that watches a directory for changes and automatically
sends files to a LaTeX compilation server whenever changes are detected.
Supports .latexignore files using gitignore syntax.
"""

import argparse
import logging
import os
import base64
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

try:
    import pathspec
except ImportError:
    print("Error: pathspec library is required. Install with: pip install pathspec")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class LatexIgnore:
    """Handles .latexignore file parsing and matching using gitignore syntax."""

    def __init__(self, root_dir: Path) -> None:
        """
        Initialize the ignore handler.

        Args:
            root_dir: Root directory to look for .latexignore
        """
        self.root_dir = root_dir
        self.spec: Optional[pathspec.PathSpec] = None
        self._load_ignore_file()

    def _load_ignore_file(self) -> None:
        """Load and parse the .latexignore file."""
        ignore_file = self.root_dir / ".latexignore"

        if not ignore_file.exists():
            logger.debug("No .latexignore file found")
            return

        try:
            with open(ignore_file, "r", encoding="utf-8") as f:
                patterns = []
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        patterns.append(line)

                if patterns:
                    self.spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
                    logger.info(f"Loaded {len(patterns)} ignore patterns from .latexignore")
                else:
                    logger.info("No patterns found in .latexignore")

        except Exception as e:
            logger.error(f"Error loading .latexignore: {e}")

    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored.

        Args:
            path: Path to check (relative to root_dir)

        Returns:
            True if the path should be ignored
        """
        if self.spec is None:
            return False

        try:
            # Get relative path from root directory
            rel_path = path.relative_to(self.root_dir)
            return self.spec.match_file(str(rel_path))
        except ValueError:
            # Path is not relative to root_dir
            return False


class LatexWatcher(FileSystemEventHandler):
    """Watches for file changes and triggers compilation."""

    def __init__(
        self,
        main_file: Path,
        root_dir: Path,
        server_url: str,
        debounce_seconds: float = 1.0,
    ) -> None:
        """
        Initialize the watcher.

        Args:
            main_file: Path to the main LaTeX file
            root_dir: Root directory to watch
            server_url: URL of the compilation server
            debounce_seconds: Time to wait before triggering compilation
        """
        super().__init__()
        self.main_file = main_file
        self.root_dir = root_dir
        self.server_url = server_url
        self.debounce_seconds = debounce_seconds
        self.ignore_handler = LatexIgnore(root_dir)

        self._pending_compile = False
        self._last_event_time = 0.0
        self._compiling = False

        # Common patterns to always ignore
        self._always_ignore = {
            ".git",
            ".svn",
            "__pycache__",
            ".DS_Store",
            "*.aux",
            "*.log",
            "*.out",
            "*.toc",
            "*.bbl",
            "*.blg",
            "*.fdb_latexmk",
            "*.fls",
            "*.synctex.gz",
            "*.pdf",  # Don't watch generated PDFs
        }

    def _should_ignore_path(self, path: Path) -> bool:
        """
        Check if a path should be ignored.

        Args:
            path: Path to check

        Returns:
            True if the path should be ignored
        """
        # Check if it's a temporary file or backup
        if path.name.startswith(".") or path.name.endswith("~"):
            return True

        # Check always-ignore patterns
        for pattern in self._always_ignore:
            if pattern.startswith("*."):
                # Check extension
                if path.suffix == pattern[1:]:
                    return True
            elif pattern in path.parts:
                return True

        # Check .latexignore
        if self.ignore_handler.should_ignore(path):
            logger.debug(f"Ignored by .latexignore: {path}")
            return True

        return False

    def _collect_files(self) -> Dict[str, Any]:
        """
        Collect all files in the directory that should be sent.
        Returns a dictionary mapping paths to file contents.
        Supports both text and binary files (binary as base64).
        """
        files = {}

        # Read main file (always text)
        try:
            with open(self.main_file, "r", encoding="utf-8") as f:
                files["main"] = f.read()
            logger.debug(f"Read main file: {self.main_file}")
        except Exception as e:
            logger.error(f"Error reading main file: {e}")
            return {}

        # Add other files dictionary
        files["files"] = {}

        # Collect all other files
        for file_path in self.root_dir.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip the main file
            if file_path == self.main_file:
                continue

            # Check ignore patterns
            if self._should_ignore_path(file_path):
                continue

            rel_path = file_path.relative_to(self.root_dir)

            # Try to read as UTF-8
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    files["files"][str(rel_path)] = {
                        "data": f.read(),
                        "binary": False
                    }
                    logger.debug(f"Added text file: {rel_path}")
                continue

            except UnicodeDecodeError:
                # Binary file → read raw and encode
                try:
                    with open(file_path, "rb") as f:
                        raw = f.read()
                        b64 = base64.b64encode(raw).decode("ascii")

                        files["files"][str(rel_path)] = {
                            "data": b64,
                            "binary": True
                        }

                        logger.debug(f"Added binary file: {rel_path}")

                except Exception as e:
                    logger.warning(f"Error reading binary {file_path}: {e}")
                    continue

            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
                continue

        return files

    def _compile(self) -> None:
        """Send files to the compilation server."""
        if self._compiling:
            logger.debug("Already compiling, skipping")
            return

        self._compiling = True
        self._pending_compile = False

        try:
            logger.info("Collecting files...")
            files = self._collect_files()

            if not files:
                logger.error("No files to compile")
                return

            logger.info(f"Sending {len(files)} file(s) to server...")

            # Send compilation request
            response = requests.post(
                f"{self.server_url}/compile",
                json=files,
                timeout=120,  # 2 minute timeout
            )

            if response.status_code == 200:
                result = response.json()

                # Check if PDF was generated
                if result.get("file"):
                    # Save PDF to disk
                    import base64

                    pdf_bytes = base64.b64decode(result["file"])
                    output_file = self.root_dir / f"{self.main_file.stem}.pdf"

                    with open(output_file, "wb") as f:
                        f.write(pdf_bytes)

                    logger.info(f"✓ Compilation successful! PDF saved to: {output_file}")
                else:
                    logger.error("✗ Compilation failed - no PDF generated")
                    # Show last 10 lines of log
                    log_lines = result.get("log", "").split("\n")
                    relevant_lines = [
                        line for line in log_lines[-20:] if line.strip() and "error" in line.lower()
                    ]
                    if relevant_lines:
                        logger.error("Recent errors:")
                        for line in relevant_lines[-10:]:
                            logger.error(f"  {line}")

            else:
                logger.error(f"Server error: {response.status_code}")
                logger.error(response.text)

        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to server at {self.server_url}")
            logger.error("Make sure the LaTeX compilation server is running")
        except requests.exceptions.Timeout:
            logger.error("Compilation timed out")
        except Exception as e:
            logger.error(f"Error during compilation: {e}")
        finally:
            self._compiling = False

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Check if should be ignored
        if self._should_ignore_path(path):
            return

        logger.debug(f"File modified: {path}")

        # Mark compilation as pending
        self._pending_compile = True
        self._last_event_time = time.time()

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        self.on_modified(event)

    def check_and_compile(self) -> None:
        """Check if compilation should be triggered (debounced)."""
        if not self._pending_compile:
            return

        # Check if enough time has passed since last event
        if time.time() - self._last_event_time < self.debounce_seconds:
            return

        # Trigger compilation
        self._compile()


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Watch LaTeX files and automatically compile on changes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "main_file",
        type=Path,
        help="Main LaTeX file to compile",
    )

    parser.add_argument(
        "--server",
        "-s",
        default="http://localhost:9080",
        help="URL of the LaTeX compilation server",
    )

    parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        default=None,
        help="Directory to watch (defaults to directory of main file)",
    )

    parser.add_argument(
        "--debounce",
        "-b",
        type=float,
        default=1.0,
        help="Seconds to wait before compiling after a change",
    )

    parser.add_argument(
        "--compile-on-start",
        "-c",
        action="store_true",
        help="Compile immediately on start",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Configure logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Resolve main file path
    main_file = args.main_file.resolve()

    if not main_file.exists():
        logger.error(f"Main file not found: {main_file}")
        sys.exit(1)

    if not main_file.is_file():
        logger.error(f"Main file is not a file: {main_file}")
        sys.exit(1)

    # Determine watch directory
    if args.directory:
        watch_dir = args.directory.resolve()
    else:
        watch_dir = main_file.parent

    if not watch_dir.exists():
        logger.error(f"Watch directory not found: {watch_dir}")
        sys.exit(1)

    if not watch_dir.is_dir():
        logger.error(f"Watch directory is not a directory: {watch_dir}")
        sys.exit(1)

    # Check if main file is in watch directory
    try:
        main_file.relative_to(watch_dir)
    except ValueError:
        logger.error("Main file must be inside watch directory")
        logger.error(f"Main file: {main_file}")
        logger.error(f"Watch dir: {watch_dir}")
        sys.exit(1)

    # Verify server is accessible
    try:
        logger.info(f"Checking server at {args.server}...")
        response = requests.get(args.server, timeout=5)
        if response.status_code == 200:
            logger.info("✓ Server is accessible")
        else:
            logger.warning(f"Server returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to server at {args.server}")
        logger.error("Make sure the LaTeX compilation server is running")
        sys.exit(1)
    except Exception as e:
        logger.warning(f"Server check failed: {e}")

    # Create watcher
    logger.info(f"Watching: {watch_dir}")
    logger.info(f"Main file: {main_file.name}")
    logger.info(f"Server: {args.server}")
    logger.info(f"Debounce: {args.debounce}s")

    watcher = LatexWatcher(
        main_file=main_file,
        root_dir=watch_dir,
        server_url=args.server,
        debounce_seconds=args.debounce,
    )

    # Compile on start if requested
    if args.compile_on_start:
        logger.info("Compiling on start...")
        watcher._compile()

    # Set up file system observer
    observer = Observer()
    observer.schedule(watcher, str(watch_dir), recursive=True)
    observer.start()

    logger.info("Watching for changes... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(0.1)
            watcher.check_and_compile()
    except KeyboardInterrupt:
        logger.info("Stopping...")
        observer.stop()

    observer.join()
    logger.info("Stopped")


if __name__ == "__main__":
    main()