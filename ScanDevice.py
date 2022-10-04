from PySide6.QtCore import Qt, Slot

from PySide6.QtWidgets import QDialog, QListWidgetItem, QListWidget, QMenu

from PySide6.QtBluetooth import (QBluetoothDeviceDiscoveryAgent, QBluetoothLocalDevice, 
                                QBluetoothDeviceInfo, QLowEnergyController)

from ui_device import Ui_DeviceDiscovery
from MyService import ServiceDiscoveryDialog

class DeviceDiscoveryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._ui = Ui_DeviceDiscovery()
        self._ui.setupUi(self)

        self._ui.scan.clicked.connect(self.startScan)

        self._local_device = QBluetoothLocalDevice()
        self._controller = QLowEnergyController()
        self._discovery_agent = QBluetoothDeviceDiscoveryAgent()
        self._deviceInfo = QBluetoothDeviceInfo()
        self._discovery_agent.deviceDiscovered.connect(self.DeviceDiscoverd)
        self._discovery_agent.finished.connect(self.ScanFinished)

        self._ui.list.itemActivated.connect(self.item_activated)

        self.devDic = {}
    
    def startScan(self):
        self._discovery_agent.start()
        self._ui.scan.setEnabled(False)
    
    @Slot(QBluetoothDeviceInfo)
    def DeviceDiscoverd(self, info):
        adrstr = info.address().toString()
        devInfo = f"{info.name()}"
        items = self._ui.list.findItems(devInfo, Qt.MatchExactly)
        if not items:
            item = QListWidgetItem(devInfo)
            self._ui.list.addItem(item)
            self.devDic[devInfo] = info
    
    def ScanFinished(self):
        self._ui.scan.setEnabled(True)

    @Slot(QListWidgetItem)
    def item_activated(self, item):
        
        deviceInfo = self.devDic[item.text()]
        name = deviceInfo.name()
        address = deviceInfo.address().toString()

        print(name)
        d = ServiceDiscoveryDialog(deviceInfo)
        d.exec()

    #     central = self._controller.createCentral(deviceInfo)
    #     central.connected.connect(self.connected)
    #     central.connectToDevice()
    
    # def connected(self):
    #     print("connected to device")
        