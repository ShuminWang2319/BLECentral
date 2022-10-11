from PySide6.QtCore import Qt, Slot,QByteArray, QAbstractListModel
from PySide6.QtWidgets import QDialog

from PySide6.QtBluetooth import (QLowEnergyController, 
                                QBluetoothUuid, 
                                QLowEnergyService)

from ui_Myservice import Ui_ServiceDiscovery

"""UUIDs for services & characteristic"""

ServiceUUID_NordicUART = '{6e400001-b5a3-f393-e0a9-e50e24dcca9e}'  
CharUUID_UARTtx = '{6e400003-b5a3-f393-e0a9-e50e24dcca9e}'
CharUUID_UARTrx = '{6e400002-b5a3-f393-e0a9-e50e24dcca9e}'

ServiceUUID_DevInfo = '{0000180a-0000-1000-8000-00805f9b34fb}'

class ServiceModel(QAbstractListModel):
    def __init__(self, service = None):
        super().__init__()
        self.service = service or []
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            status, uuid, name, service = self.service[index.row()]
            return f"{uuid} {name}"
    
    def rowCount(self, index):
        return len(self.service)


class ServiceDiscoveryDialog(QDialog):
    def __init__(self, deviceInfo, parent=None):
        super().__init__(parent)
        self._ui = Ui_ServiceDiscovery()
        self._ui.setupUi(self)

        self.setWindowTitle(deviceInfo.name())

        self.model = ServiceModel()
        self._ui.servicelistView.setModel(self.model)
        self._ui.connect.pressed.connect(self.connectService)
        
        self._controller = QLowEnergyController()
        self.central = self._controller.createCentral(deviceInfo)
        print("Connecting to device")
        self.central.connectToDevice()
        self.central.connected.connect(self.connected)

        self._ui.send.setEnabled(False)

        self._ui.send.clicked.connect(self.UARTsend)

        self.UartRX = 0
      

    def connected(self):
        print("connected to device")
        
        print("Discovering services")
        self.central.discoverServices()
        self.central.serviceDiscovered.connect(self.ServiceDiscovered)

    
    @Slot(QBluetoothUuid)
    def ServiceDiscovered(self,uuid):
        
        service = self.central.createServiceObject(uuid)
        suuidstr = service.serviceUuid().toString()
        sname = service.serviceName()       

        self.model.service.append((False, suuidstr, sname, service))
        self.model.layoutChanged.emit()

        print("serviceDiscovered:"+ f"{suuidstr} {sname}")

    def connectService(self):
        indexes = self._ui.servicelistView.selectedIndexes()
        #print(indexes)
        if indexes:
            index = indexes[0]
            item = self.model.service[index.row()]
            uuid = item[1]
            service = item[3]
            # print("item: ")
            # print(item)
            # print(item[1])
            
            mode = QLowEnergyService.DiscoveryMode.FullDiscovery
            service.discoverDetails(mode)
            service.stateChanged.connect(self.StateChanged)

    def StateChanged(self, newState):
        #print(newState)
        if newState == QLowEnergyService.ServiceState.RemoteServiceDiscovered:

            indexes = self._ui.servicelistView.selectedIndexes()
            index = indexes[0]
            item = self.model.service[index.row()]
            uuid = item[1]
            service = item[3]

            if uuid == ServiceUUID_NordicUART:
                print("nordic UART service")
                
                characteristics = service.characteristics()
                #print(characteristics)
                for c in characteristics:

                    #{6e400003-b5a3-f393-e0a9-e50e24dcca9e} UART TX
                    if c.uuid().toString() == CharUUID_UARTtx:
                        UartTX = c
                        print('Characteristic: UartTX')
                    #{6e400002-b5a3-f393-e0a9-e50e24dcca9e} UART RX
                    if c.uuid().toString() == CharUUID_UARTrx:
                        self.UartRX = c
                        print('Characteristic: UartRX')
                
                
                #enable notify
                CCCD = UartTX.clientCharacteristicConfiguration()
                data = QByteArray(b'\x01\x00')
                service.writeDescriptor(CCCD,data)
                
                self._ui.send.setEnabled(True)
                # service.characteristicChanged.connect(self.readUartTX)
                self._ui.lineEdit.returnPressed.connect(self.UARTsend)

            elif uuid == ServiceUUID_DevInfo:
                print("Device Information service")
                         
                characteristics = service.characteristics()
                for c in characteristics:
                    print(c.name())
                    print(c.value())
                    print(c.properties())

        # else:
        
    
    def readUartTX(self,c,value):
        
        #print(c.uuid())
        print('RX:')
        print(value)
    
    def UARTsend(self):
        #print('send pushed')
        
        #instr = 'G/test/led'
        instr = self._ui.lineEdit.text()
        inbyte = instr.encode()
        inbyte = QByteArray(inbyte)
        print("TX:")
        print(instr)

        indexes = self._ui.servicelistView.selectedIndexes()
        index = indexes[0]
        item = self.model.service[index.row()]
        service = item[3]

        service.characteristicChanged.connect(self.readUartTX)
        
        service.writeCharacteristic(self.UartRX,inbyte)

