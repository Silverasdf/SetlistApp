from gui import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SetlistGeneratorWindow()
    sys.exit(app.exec_())