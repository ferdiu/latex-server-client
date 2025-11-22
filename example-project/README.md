# Example Project Setup

This guide shows how to set up a complete LaTeX project with auto-compilation using the latex-server package.

## Project Structure

Let's create a research paper project:

```
my-paper/
├── main.tex                 # Main document
├── .latexignore            # Files to ignore
├── abstract.tex            # Abstract
├── introduction.tex        # Introduction section
├── methods.tex             # Methods section
├── results.tex             # Results section
├── conclusion.tex          # Conclusion
├── references.bib          # Bibliography
└── tables/                 # Tables directory
    └── results.tex
```

## Step 1: Start the Server

In Terminal 1:

```bash
# Start the LaTeX compilation server
latex-server

# You should see:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:9080
```

## Step2: Start the Watcher

In Terminal 2:

```bash
# Navigate to your project
cd example-project

# Start watching with initial compilation
latex-watch main.tex --compile-on-start --verbose

# You should see:
# 13:45:23 - INFO - Checking server at http://localhost:9080...
# 13:45:23 - INFO - ✓ Server is accessible
# 13:45:23 - INFO - Watching: /path/to/my-paper
# 13:45:23 - INFO - Main file: main.tex
# 13:45:23 - INFO - Server: http://localhost:9080
# 13:45:23 - INFO - Debounce: 1.0s
# 13:45:23 - INFO - Compiling on start...
# 13:45:23 - INFO - Collecting files...
# 13:45:23 - INFO - Sending 8 file(s) to server...
# 13:45:25 - INFO - ✓ Compilation successful! PDF saved to: /path/to/my-paper/main.pdf
# 13:45:25 - INFO - Watching for changes... (Press Ctrl+C to stop)
```

## Step 3: Edit and Watch

Now you can make changes to the files and watch it automatically recompile your project.

# Summary

The `latex-watch` command provides a modern, efficient workflow for LaTeX document writing:

1. **Start once**: `latex-server` in one terminal
2. **Watch**: `latex-watch main.tex` in another
3. **Edit**: Use any editor you prefer
4. **Save**: Automatic compilation
5. **View**: PDF updates automatically

This eliminates the traditional edit-compile-view cycle and lets you focus on writing!

## Next Steps

- Read [WATCH_USAGE.md](WATCH_USAGE.md) for complete documentation
- Check [README.md](README.md) for API usage
- See [SETUP.md](SETUP.md) for development setup