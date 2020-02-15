from gui import *
import sys

def main():
    config = Config("config.json")

    app = QApplication(sys.argv)
    gallery = Builder(config)
    gallery.resize(800, 600)
    gallery.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()