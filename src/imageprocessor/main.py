import sys

from PySide6.QtWidgets import QApplication

from .ui import MainWindow


def run():
    app = QApplication(sys.argv)

    app_screen = app.primaryScreen()

    screen_size = (800, 600)  # Default size
    if app_screen is not None:
        screen_geometry = app_screen.geometry()
        screen_size = (screen_geometry.width(), screen_geometry.height())

    window = MainWindow(size=screen_size)
    window.show()
    app.exec()


if __name__ == "__main__":
    run()
