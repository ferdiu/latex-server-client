"""
Tests for the LaTeX watch functionality.

Run with: pytest tests/test_watch.py -v
"""

import tempfile
from pathlib import Path

import pytest

from latex_server_client.latex_watch import LatexIgnore


class TestLatexIgnore:
    """Tests for the LatexIgnore class."""

    def test_no_ignore_file(self) -> None:
        """Test behavior when no .latexignore file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ignore = LatexIgnore(root)

            # Should not ignore anything
            test_file = root / "test.tex"
            assert not ignore.should_ignore(test_file)

    def test_simple_pattern(self) -> None:
        """Test simple filename pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create .latexignore
            ignore_file = root / ".latexignore"
            ignore_file.write_text("*.aux\n*.log\n")

            ignore = LatexIgnore(root)

            # Should ignore .aux and .log files
            assert ignore.should_ignore(root / "main.aux")
            assert ignore.should_ignore(root / "main.log")
            assert not ignore.should_ignore(root / "main.tex")

    def test_directory_pattern(self) -> None:
        """Test directory pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create .latexignore
            ignore_file = root / ".latexignore"
            ignore_file.write_text("build/\n")

            ignore = LatexIgnore(root)

            # Should ignore files in build directory
            assert ignore.should_ignore(root / "build" / "main.pdf")
            assert not ignore.should_ignore(root / "main.tex")

    def test_nested_pattern(self) -> None:
        """Test nested directory pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create .latexignore
            ignore_file = root / ".latexignore"
            ignore_file.write_text("**/*.aux\n")

            ignore = LatexIgnore(root)

            # Should ignore .aux files in any directory
            assert ignore.should_ignore(root / "main.aux")
            assert ignore.should_ignore(root / "chapters" / "chapter1.aux")
            assert not ignore.should_ignore(root / "main.tex")

    def test_comments_and_empty_lines(self) -> None:
        """Test that comments and empty lines are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create .latexignore with comments
            ignore_file = root / ".latexignore"
            ignore_file.write_text(
                """
# This is a comment
*.aux

# Another comment
*.log
"""
            )

            ignore = LatexIgnore(root)

            # Should only ignore .aux and .log
            assert ignore.should_ignore(root / "main.aux")
            assert ignore.should_ignore(root / "main.log")
            assert not ignore.should_ignore(root / "main.tex")

    def test_negation_pattern(self) -> None:
        """Test negation pattern (gitignore feature)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create .latexignore with negation
            ignore_file = root / ".latexignore"
            ignore_file.write_text(
                """*.pdf
!important.pdf
"""
            )

            ignore = LatexIgnore(root)

            # Should ignore all PDFs except important.pdf
            assert ignore.should_ignore(root / "main.pdf")
            assert not ignore.should_ignore(root / "important.pdf")

    def test_specific_file(self) -> None:
        """Test ignoring a specific file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create .latexignore
            ignore_file = root / ".latexignore"
            ignore_file.write_text("temp.tex\n")

            ignore = LatexIgnore(root)

            # Should ignore only temp.tex
            assert ignore.should_ignore(root / "temp.tex")
            assert not ignore.should_ignore(root / "main.tex")

    def test_subdirectory_gitignore_syntax(self) -> None:
        """Test subdirectory patterns using gitignore syntax."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create .latexignore
            ignore_file = root / ".latexignore"
            ignore_file.write_text(
                """
# Ignore everything in build directory
build/

# Ignore all tex files in temp directory
temp/*.tex

# Ignore all files in any __pycache__ directory
**/__pycache__/
"""
            )

            ignore = LatexIgnore(root)

            # Test build directory
            assert ignore.should_ignore(root / "build" / "main.pdf")
            assert ignore.should_ignore(root / "build" / "subdir" / "file.aux")

            # Test temp directory
            assert ignore.should_ignore(root / "temp" / "test.tex")
            assert not ignore.should_ignore(root / "temp" / "test.bib")

            # Test __pycache__
            assert ignore.should_ignore(root / "__pycache__" / "test.pyc")
            assert ignore.should_ignore(root / "subdir" / "__pycache__" / "test.pyc")

    def test_path_outside_root(self) -> None:
        """Test that paths outside root directory are not ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            root.mkdir()

            # Create .latexignore
            ignore_file = root / ".latexignore"
            ignore_file.write_text("*.aux\n")

            ignore = LatexIgnore(root)

            # Path outside root should not be ignored (returns False)
            outside_path = Path(tmpdir) / "outside.aux"
            assert not ignore.should_ignore(outside_path)


class TestLatexWatcherHelpers:
    """Tests for LatexWatcher helper methods."""

    def test_should_ignore_temporary_files(self) -> None:
        """Test that temporary files are always ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            main_file = root / "main.tex"
            main_file.write_text("")

            from latex_server_client.latex_watch import LatexWatcher

            watcher = LatexWatcher(main_file, root, "http://localhost:9080")

            # Temporary files should be ignored
            assert watcher._should_ignore_path(root / ".hidden")
            assert watcher._should_ignore_path(root / "file~")
            assert watcher._should_ignore_path(root / "main.aux")
            assert watcher._should_ignore_path(root / "main.log")
            assert watcher._should_ignore_path(root / "main.pdf")

            # Normal files should not be ignored
            assert not watcher._should_ignore_path(root / "main.tex")
            assert not watcher._should_ignore_path(root / "refs.bib")

    def test_should_ignore_git_directory(self) -> None:
        """Test that .git directory is always ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            main_file = root / "main.tex"
            main_file.write_text("")

            from latex_server_client.latex_watch import LatexWatcher

            watcher = LatexWatcher(main_file, root, "http://localhost:9080")

            # .git files should be ignored
            assert watcher._should_ignore_path(root / ".git" / "config")
            assert watcher._should_ignore_path(root / ".git" / "HEAD")

    def test_collect_files_basic(self) -> None:
        """Test basic file collection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files
            main_file = root / "main.tex"
            main_file.write_text("\\documentclass{article}")

            content_file = root / "content.tex"
            content_file.write_text("Hello world")

            from latex_server_client.latex_watch import LatexWatcher

            watcher = LatexWatcher(main_file, root, "http://localhost:9080")

            files = watcher._collect_files()

            # Should have main and content files
            assert "main" in files
            assert "files" in files
            assert "content.tex" in files["files"]
            assert files["main"] == "\\documentclass{article}"
            assert files["files"]["content.tex"] == "Hello world"

    def test_collect_files_with_subdirectory(self) -> None:
        """Test file collection with subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files
            main_file = root / "main.tex"
            main_file.write_text("main")

            # Create subdirectory
            chapters_dir = root / "chapters"
            chapters_dir.mkdir()

            chapter1 = chapters_dir / "chapter1.tex"
            chapter1.write_text("chapter 1")

            from latex_server_client.latex_watch import LatexWatcher

            watcher = LatexWatcher(main_file, root, "http://localhost:9080")

            files = watcher._collect_files()

            # Should preserve directory structure
            assert "main" in files
            assert "files" in files
            assert "chapters/chapter1.tex" in files["files"] or "chapters\\chapter1.tex" in files["files"]

    def test_collect_files_ignores_binary(self) -> None:
        """Test that binary files are ignored during collection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create text file
            main_file = root / "main.tex"
            main_file.write_text("main")

            # Create binary file
            binary_file = root / "image.png"
            binary_file.write_bytes(b"\x89PNG\r\n\x1a\n")

            from latex_server_client.latex_watch import LatexWatcher

            watcher = LatexWatcher(main_file, root, "http://localhost:9080")

            files = watcher._collect_files()

            # Should only have text files
            assert "main" in files
            assert "image.png" not in files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])