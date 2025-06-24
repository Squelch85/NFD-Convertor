# NFD-Convertor

A simple utility to convert file and folder names from Apple's NFD encoding
into standard NFC form. It provides both a drag-and-drop GUI and a command
line interface.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI

Run the application without arguments to launch the drag-and-drop GUI:

```bash
python NFD_Convertor.py
```

### Command line

Pass one or more paths with `--cli` (or just provide paths) to perform a
conversion without the GUI:

```bash
python NFD_Convertor.py --cli /path/to/folder /path/to/file
```

## Packaging

A PyInstaller spec file is included. Build a standalone executable with:

```bash
pyinstaller NFD_Convertor.spec
```

## Running Tests

```bash
pytest
```

## Notes

On Windows and macOS the bundled `tkinterdnd2` package is required for native
file drag-and-drop support.
