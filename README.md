# LaTeX Compilation Client (for LaTeX Compilation Server)

The `latex-watch` command monitors your LaTeX project directory and automatically compiles your document whenever files change. This provides a live-preview workflow where you can edit your LaTeX files and immediately see the updated PDF.

## Features

- **BibTeX Support**: Automatically runs BibTeX when citations are detected
- **Multi-file Projects**: Support for projects with multiple `.tex` files, bibliographies, and resources
- **Auto-Watch Mode**: Watch directory for changes and auto-compile with `latex-watch` command
- **.latexignore Support**: Exclude files using gitignore syntax
- **Comprehensive Logging**: Detailed compilation logs for debugging
- **Production Ready**: Includes health checks, proper error handling, and security best practices
- **Fully Tested**: Comprehensive test suite with pytest
- **Standalone Package**: Installable Python package with proper packaging

## Installation

The `latex-watch` command is included when you install the latex-server package:

```bash
pip install -e .
```

## Quick Start

1. **Start the LaTeX compilation server** (in one terminal):
```bash
latex-server
```

2. **Start watching your LaTeX project** (in another terminal):
```bash
latex-watch main.tex
```

Now edit any `.tex` file in your project, and the PDF will automatically recompile!

## Usage

### Basic Usage

```bash
latex-watch main.tex
```

This will:
- Watch the directory containing `main.tex`
- Monitor all files in that directory (and subdirectories)
- Automatically compile when any file changes
- Save the compiled PDF as `main.pdf` in the same directory

### Custom Server URL

If your compilation server is running on a different host/port:

```bash
latex-watch main.tex --server http://192.168.1.100:9080
```

### Custom Watch Directory

Watch a specific directory instead of the main file's directory:

```bash
latex-watch main.tex --directory /path/to/project
```

### Compile on Start

Compile immediately when starting the watcher:

```bash
latex-watch main.tex --compile-on-start
```

### Adjust Debounce Time

Control how long to wait after a change before compiling (in seconds):

```bash
latex-watch main.tex --debounce 2.0
```

This is useful if you're making many rapid changes and want to avoid triggering compilation too frequently.

### Verbose Output

See detailed information about file watching and compilation:

```bash
latex-watch main.tex --verbose
```

## Command-Line Options

```
usage: latex-watch [-h] [--server SERVER] [--directory DIRECTORY]
                   [--debounce DEBOUNCE] [--compile-on-start]
                   [--verbose] [--version]
                   main_file

Watch LaTeX files and automatically compile on changes

positional arguments:
  main_file             Main LaTeX file to compile

options:
  -h, --help            show this help message and exit
  --server SERVER, -s SERVER
                        URL of the LaTeX compilation server
                        (default: http://localhost:9080)
  --directory DIRECTORY, -d DIRECTORY
                        Directory to watch (defaults to directory of main file)
  --debounce DEBOUNCE, -b DEBOUNCE
                        Seconds to wait before compiling after a change
                        (default: 1.0)
  --compile-on-start, -c
                        Compile immediately on start (default: False)
  --verbose, -v         Enable verbose logging (default: False)
  --version             show program's version number and exit
```

## .latexignore File

Create a `.latexignore` file in your project directory to exclude files from being sent to the compilation server. The syntax follows the same rules as `.gitignore`.

### Example .latexignore

```gitignore
# Ignore LaTeX auxiliary files (already ignored by default)
*.aux
*.log
*.out
*.toc
*.bbl
*.blg

# Ignore build directory
build/

# Ignore specific files
notes.tex
scratch.tex

# Ignore all files in a subdirectory
drafts/*

# Ignore all PDFs except the important one
*.pdf
!final-version.pdf

# Ignore temporary files
*~
*.swp
.DS_Store

# Ignore version control
.git/
.svn/
```

### Default Ignored Files

Even without a `.latexignore` file, the following are always ignored:

- Hidden files (starting with `.`)
- Backup files (ending with `~`)
- LaTeX auxiliary files: `.aux`, `.log`, `.out`, `.toc`, `.bbl`, `.blg`, `.fdb_latexmk`, `.fls`, `.synctex.gz`
- Generated PDFs (`.pdf`)
- Version control directories: `.git`, `.svn`
- Python cache: `__pycache__`
- System files: `.DS_Store`

## .latexignore Syntax

The `.latexignore` file supports standard gitignore patterns:

### Wildcards

- `*` matches any number of characters (except `/`)
- `?` matches any single character
- `**` matches any number of directories

### Examples

```gitignore
# Ignore all .aux files in any directory
**/*.aux

# Ignore all files in build directory
build/

# Ignore specific file
temp.tex

# Ignore all .log files at root level only
/*.log

# Ignore everything in drafts directory
drafts/*

# Ignore files matching pattern
chapter-*.tex
```

### Negation

Use `!` to negate a pattern:

```gitignore
# Ignore all PDFs
*.pdf

# Except this one
!important.pdf
```

### Comments

Lines starting with `#` are comments:

```gitignore
# This is a comment
*.aux  # This is also a comment
```

## Workflow Examples

### Basic Writing Workflow

1. **Terminal 1** - Start the server:
```bash
latex-server
```

2. **Terminal 2** - Start watching:
```bash
cd my-paper
latex-watch main.tex --compile-on-start
```

3. Edit your LaTeX files in your favorite editor
4. Save any file
5. Watch the terminal for compilation status
6. Open `main.pdf` in a PDF viewer that auto-refreshes

### Multi-Chapter Book

Project structure:
```
my-book/
├── main.tex
├── chapters/
│   ├── chapter1.tex
│   ├── chapter2.tex
│   └── chapter3.tex
├── images/
│   └── diagram.png
└── references.bib
```

Usage:
```bash
cd my-book
latex-watch main.tex
```

All files in `chapters/`, `images/`, and the `references.bib` will be monitored.

### With Custom Ignore Rules

Create `.latexignore`:
```gitignore
# Ignore drafts
drafts/

# Ignore notes
*-notes.tex

# Ignore old versions
old-versions/
```

Then run:
```bash
latex-watch main.tex --verbose
```

### Remote Server

If your LaTeX server is running on another machine:

```bash
latex-watch main.tex --server http://latex-server.local:9080
```

### Fast Editing (Longer Debounce)

If you're making rapid changes and want to compile less frequently:

```bash
latex-watch main.tex --debounce 3.0
```

This will wait 3 seconds after the last change before compiling.

## Troubleshooting

### Server Connection Error

**Error:** `Cannot connect to server at http://localhost:9080`

**Solution:** Make sure the LaTeX server is running:
```bash
latex-server
```

### Compilation Keeps Failing

**Problem:** The watcher shows compilation errors repeatedly.

**Solution:**
1. Run with `--verbose` to see detailed logs
2. Check the error messages in the terminal
3. Fix LaTeX errors in your source files
4. The watcher will automatically retry after you save fixes

### Too Many Compilation Triggers

**Problem:** Compilation triggers too frequently while editing.

**Solution:** Increase the debounce time:
```bash
latex-watch main.tex --debounce 2.0
```

### Some Files Not Being Watched

**Problem:** Changes to certain files don't trigger compilation.

**Solution:**
1. Check if they're in `.latexignore`
2. Check if they match default ignore patterns
3. Run with `--verbose` to see which files are being ignored
4. Ensure the files are within the watched directory

### Main File Not in Watch Directory

**Error:** `Main file must be inside watch directory`

**Solution:** Ensure your main LaTeX file is inside the directory you're watching:
```bash
# Correct
cd my-project
latex-watch main.tex

# Incorrect
cd /some/other/directory
latex-watch /my-project/main.tex
```

Or specify the watch directory explicitly:
```bash
latex-watch /my-project/main.tex --directory /my-project
```

### Binary Files Causing Issues

The watcher automatically skips binary files (like images) during collection. If you need to include binary files, you'll need to:

1. Keep them in the project directory (they'll be available to LaTeX during compilation)
2. Reference them normally in your LaTeX code
3. The server will have access to them during compilation

## Integration with Editors

### VS Code

Add a task to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Watch LaTeX",
      "type": "shell",
      "command": "latex-watch",
      "args": ["main.tex", "--compile-on-start"],
      "problemMatcher": [],
      "isBackground": true
    }
  ]
}
```

### Vim/Neovim

Add to your `.vimrc` or `init.vim`:

```vim
" Start LaTeX watcher
nnoremap <leader>lw :!latex-watch % --compile-on-start &<CR>
```

### Emacs

Add to your `.emacs` or `init.el`:

```elisp
(defun start-latex-watch ()
  "Start latex-watch for current buffer"
  (interactive)
  (start-process "latex-watch" "*latex-watch*"
                 "latex-watch" (buffer-file-name)
                 "--compile-on-start"))
```

## Tips and Best Practices

1. **Use .latexignore**: Keep your compilation fast by excluding unnecessary files

2. **Appropriate Debounce**: Set based on your editing speed
   - Fast typing: 1-2 seconds
   - Deliberate editing: 0.5-1 seconds
   - Slow machine: 2-3 seconds

3. **Auto-Refreshing PDF Viewer**: Use a PDF viewer that automatically reloads when the file changes:
   - **Linux**: Evince, Okular
   - **macOS**: Skim
   - **Windows**: SumatraPDF

4. **Multiple Terminals**: Keep server and watcher in separate terminals for easy monitoring

5. **Verbose Mode for Debugging**: Use `--verbose` when setting up or troubleshooting

6. **Compile on Start**: Use `--compile-on-start` to immediately see if everything works

## Performance Considerations

- **File Count**: The watcher monitors all files recursively. Large projects with thousands of files may be slower.

- **Debounce Time**: Shorter debounce = faster response but more compilations. Longer debounce = fewer compilations but delayed response.

- **Network Latency**: If using a remote server, compilation will be slower due to network transfer time.

- **.latexignore**: Use this to exclude large directories or many files you don't need.

## Comparison with Other Tools

### vs latexmk -pvc

**latex-watch advantages:**
- Server-based compilation (works on machines without LaTeX)
- Centralized compilation server
- Web-based workflow possible
- Ignores auxiliary files automatically

**latexmk advantages:**
- No server needed
- Works offline
- More mature and battle-tested

### vs VS Code LaTeX Workshop

**latex-watch advantages:**
- Editor-agnostic
- Can use remote compilation server
- Simple and focused

**VS Code LaTeX Workshop advantages:**
- Integrated with VS Code
- More features (syntax highlighting, snippets, etc.)
- GUI configuration

## See Also

- Main README: [README.md](README.md)
- Server documentation: [SETUP.md](SETUP.md)
- API documentation: http://localhost:9080/docs (when server is running)