import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from ScanDevice import DeviceDiscoveryDialog

if __name__ == '__main__':
    app = QApplication(sys.argv)
    d = DeviceDiscoveryDialog()
    d.exec()
    sys.exit(0)