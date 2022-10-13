from PySide6.QtCore import Qt, Slot, QByteArray, QAbstractListModel
from PySide6.QtWidgets import QDialog

from PySide6.QtBluetooth import (QLowEnergyController, 
                                QBluetoothUuid, 
                                QLowEnergyService)

from ui_Myservice import Ui_ServiceDiscovery
import parser

"""UUIDs for services & characteristic"""

ServiceUUID_NordicUART = '{6e400001-b5a3-f393-e0a9-e50e24dcca9e}'  
CharUUID_UARTtx = '{6e400003-b5a3-f393-e0a9-e50e24dcca9e}'
CharUUID_UARTrx = '{6e400002-b5a3-f393-e0a9-e50e24dcca9e}'

ServiceUUID_DevInfo = '{0000180a-0000-1000-8000-00805f9b34fb}'

class serviceModel(QAbstractListModel):
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

        self.model = serviceModel()
        self._ui.servicelistView.setModel(self.model)
        self._ui.connect.pressed.connect(self.connectService)
        
        self._controller = QLowEnergyController()
        self.central = self._controller.createCentral(deviceInfo)
        print("Connecting to device")
        self.central.connectToDevice()
        self.central.connected.connect(self.connected)

        self._ui.send.setEnabled(False)
        self._ui.SendSeq.setEnabled(False)

        self.UartRX = 0

        self.apiParser = parser.APIParser()

        self.apiIdx = 0
        self.apiCnt = 0
        self.currSer = 0

    def connected(self):
        print("connected to device")
        
        print("Discovering services")
        self.central.discoverServices()
        self.central.serviceDiscovered.connect(self.serviceDiscovered)

    
    @Slot(QBluetoothUuid)
    def serviceDiscovered(self,uuid):
        
        service = self.central.createServiceObject(uuid)
        suuidstr = service.serviceUuid().toString()
        sname = service.serviceName()       

        self.model.service.append((False, suuidstr, sname, service))
        self.model.layoutChanged.emit()

        print("Service discovered:"+ f"{suuidstr} {sname}")

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
            service.stateChanged.connect(self.stateChanged)

    def stateChanged(self, newState):
        #print(newState)
        if newState == QLowEnergyService.ServiceState.RemoteServiceDiscovered:

            indexes = self._ui.servicelistView.selectedIndexes()
            index = indexes[0]
            item = self.model.service[index.row()]
            uuid = item[1]
            service = item[3]

            if uuid == ServiceUUID_NordicUART:
                print("nordic UART service")
                self._ui.textEdit.append('Nordic UART service:')
                
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
                self._ui.SendSeq.setEnabled(True)
                self._ui.send.clicked.connect(self.UARTsend)
                self._ui.SendSeq.clicked.connect(self.UARTSendSeq)
                self._ui.lineEdit.returnPressed.connect(self.UARTsend)

            elif uuid == ServiceUUID_DevInfo:
                print("Device Information service")
                self._ui.textEdit.append('Device Information service:')

                characteristics = service.characteristics()
                for c in characteristics:
                    print(c.name())
                    print(c.value())
                    print(c.properties())

                    self._ui.textEdit.append('Name: ' + str(c.name()))
                    self._ui.textEdit.append('      value: ' + str(c.value()))

        # else:
        
    """
    Send text API from line edit
    """
    def readUartTX(self,c,value):
        
        #print(c.uuid())
        print('RX:')
        print(value)
        self._ui.textEdit.append('Central RX: ' + str(value))
    
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

        try:
            service.characteristicChanged.disconnect(self.readUartTXSeq)
        except RuntimeError:
            pass

        try:
            service.characteristicChanged.disconnect(self.readUartTX)
        except RuntimeError:
            pass

        service.characteristicChanged.connect(self.readUartTX)
        
        service.writeCharacteristic(self.UartRX,inbyte)
        self._ui.textEdit.append('Central TX: ' + str(instr))

    """
    Send API from api.csv.
    Support both string and byte array format.
    """
    def UARTSendSeq(self):
        indexes = self._ui.servicelistView.selectedIndexes()
        index = indexes[0]
        item = self.model.service[index.row()]
        service = item[3]

        self.currSer = service
        
        try:
            service.characteristicChanged.disconnect(self.readUartTX)
        except RuntimeError:
            pass

        try:
            service.characteristicChanged.disconnect(self.readUartTXSeq)
        except RuntimeError:
            pass

        service.characteristicChanged.connect(self.readUartTXSeq)
 
        self.apiCnt = self.apiParser.getAPInum()
        self.apiIdx = 1
        self.UARTsendAPI(self.apiIdx)

    def readUartTXSeq(self,c,value):
        print('RX:')
        print(value)
        self._ui.textEdit.append('Central RX: ' + str(value))
        self.apiIdx += 1

        if(self.apiIdx <= self.apiCnt):
            self.UARTsendAPI(self.apiIdx)
    
    def UARTsendAPI(self, idx):
        apistr,tp,name = self.apiParser.getAPI(idx)
        if tp == 'str':
            inbyte = apistr.encode()
            inbyte = QByteArray(inbyte)
        if tp == 'ba':
            strlist = apistr.split(' ')
            print(strlist)
            bytelist = list(map(int, strlist))
            inbyte = QByteArray(bytearray(bytelist))
        
        self.currSer.writeCharacteristic(self.UartRX,inbyte)
        print('TX: ')
        print(apistr)
        print(name)
        self._ui.textEdit.append('Central TX: ' + str(apistr))
    
