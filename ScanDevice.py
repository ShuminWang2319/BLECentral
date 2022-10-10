from PySide6.QtCore import Qt, Slot, QAbstractListModel
from PySide6.QtWidgets import QDialog, QListWidgetItem, QListWidget, QMenu

from PySide6.QtBluetooth import (QBluetoothDeviceDiscoveryAgent, QBluetoothLocalDevice, 
                                QBluetoothDeviceInfo, QLowEnergyController)

from ui_device import Ui_DeviceDiscovery
from MyService import ServiceDiscoveryDialog


class DeviceModel(QAbstractListModel):
    def __init__(self, device = None):
        super().__init__()
        self.device = device or []
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            status, name, addr, info = self.device[index.row()]
            return name
    def rowCount(self, index):
        return len(self.device)


class DeviceDiscoveryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._ui = Ui_DeviceDiscovery()
        self._ui.setupUi(self)
        
        self.model = DeviceModel()
        self._ui.deviceListView.setModel(self.model)

        self._local_device = QBluetoothLocalDevice()
        self._controller = QLowEnergyController()
        self._discovery_agent = QBluetoothDeviceDiscoveryAgent()
        self._deviceInfo = QBluetoothDeviceInfo()

        self._discovery_agent.deviceDiscovered.connect(self.DeviceDiscoverd)
        self._discovery_agent.finished.connect(self.ScanFinished)

        self._ui.scan.clicked.connect(self.startScan)
        self._ui.deviceListView.activated.connect(self.item_activated)
    
    def startScan(self):
        self._discovery_agent.start()
        self._ui.scan.setEnabled(False)
    
    @Slot(QBluetoothDeviceInfo)
    def DeviceDiscoverd(self, info):
        adrstr = info.address().toString()
        dev = (False, info.name(), adrstr, info)

        if dev not in self.model.device:
            
            self.model.device.append(dev)
            self.model.layoutChanged.emit()
    
    def ScanFinished(self):
        self._ui.scan.setEnabled(True)

    @Slot(QListWidgetItem)
    def item_activated(self, item):
        indexes = self._ui.deviceListView.selectedIndexes()
        if indexes:
            item = self.model.device[indexes[0].row()]
            name = item[1]
            address = item[2]
            deviceInfo = item[3]
        print(name)
        d = ServiceDiscoveryDialog(deviceInfo)
        d.exec()
