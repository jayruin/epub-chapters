from gui import *
import sys

def main():
    library = Library("config.json")

    app = QApplication(sys.argv)
    gallery = Builder(library)
    gallery.resize(800, 600)
    gallery.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()