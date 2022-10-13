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
        
        self._ui.scan.setEnabled(False)
        
        self._ui.power.setCheckState(Qt.Unchecked)
        self._ui.discoverable.setCheckState(Qt.Unchecked) #unused currently
        self._ui.power.stateChanged.connect(self.checkLocalDevice)

        self.model = DeviceModel()
        self._ui.deviceListView.setModel(self.model)

        self._local_device = QBluetoothLocalDevice()
        self.discoveryAgent = 0 

        self._ui.scan.clicked.connect(self.startScanning)
        self._ui.deviceListView.activated.connect(self.itemActivated)
        self._ui.connectDevice.clicked.connect(self.itemActivated)

        self._ui.clear.clicked.connect(self.clearList)


    def checkLocalDevice(self):
        if self._ui.power.checkState() == Qt.Checked:
            if self._local_device.isValid() == True:
                self._local_device.powerOn()
                name = self._local_device.name()
                print(name)
                
                # if self._ui.discoverable.checkState() == Qt.Checked:
                self._local_device.setHostMode(self._local_device.HostDiscoverable)
                
                self._ui.scan.setEnabled(True)
        else:
            print("power on unchecked")

    def startScanning(self):
        self.discoveryAgent = QBluetoothDeviceDiscoveryAgent()
        self.discoveryAgent.deviceDiscovered.connect(self.deviceDiscoverd)
        self.discoveryAgent.finished.connect(self.scanFinished)
        self.discoveryAgent.canceled.connect(self.scanCanceled)

        self.discoveryAgent.start()
        self._ui.scan.setEnabled(False)
        self._ui.clear.setEnabled(False)
        self._ui.stopScanPB.clicked.connect(self.discoveryAgent.stop)
    
    def scanCanceled(self):
        #print("scanCanceled")
        self._ui.scan.setEnabled(True)
        self._ui.clear.setEnabled(True)

    def clearList(self):
        self.model.device = []
        self.model.layoutChanged.emit()
    
    @Slot(QBluetoothDeviceInfo)
    def deviceDiscoverd(self, info):
        adrStr = info.address().toString()
        dev = (False, info.name(), adrStr, info)

        if dev not in self.model.device:
            
            self.model.device.append(dev)
            self.model.layoutChanged.emit()
    
    def scanFinished(self):
        self._ui.scan.setEnabled(True)
        self._ui.clear.setEnabled(True)

    @Slot(QListWidgetItem)
    def itemActivated(self, item):
        indexes = self._ui.deviceListView.selectedIndexes()
        if indexes:
            item = self.model.device[indexes[0].row()]
            name = item[1]
            address = item[2]
            deviceInfo = item[3]
        print(name)
        d = ServiceDiscoveryDialog(deviceInfo)
        d.exec()
