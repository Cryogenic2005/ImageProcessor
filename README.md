# Image Processor

A small interactive image-processing application developed with Python, PySide6, NumPy, Pillow, and OpenCV.

This application was developed for Assignment 1 submission for NTU module SC4061 - Computer Vision.

## Running from Source

This project uses [uv](https://docs.astral.sh/uv/) for Python environment and dependency management.

Install [uv](https://docs.astral.sh/uv/) if it is not already installed, then run:

```bash
uv sync
uv run app
```

The application should launch directly. Images can be loaded using **Change Image**, and transformations can be added and configured from the control panel.

## Compiling the Application

The application can be packaged into a standalone executable using PyInstaller.

First, install the project dependencies and development dependencies:

```bash
uv sync
```

Then build the executable:

```bash
uv run pyinstaller ImageProcessor.spec
```

The compiled application will be placed in the `dist/` directory.

To run the compiled application, open:

```text
dist/ImageProcessor/ImageProcessor.exe
```

The compiled application does not require Python or the project's dependencies to be installed separately.

## Project Structure

```text
src/imageprocessor/
├── main.py
├── ui/
└── transforms/
```

* `src/imageprocessor/` — application source code
* `src/imageprocessor/ui/` — graphical user interface
* `src/imageprocessor/transforms/` — image-processing transformations
