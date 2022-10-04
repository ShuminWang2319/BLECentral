from turtle import delay
from PySide6.QtCore import Qt, Slot,QByteArray
from PySide6.QtWidgets import QDialog,QListWidgetItem

from PySide6.QtBluetooth import (QLowEnergyController, 
                                QBluetoothServiceDiscoveryAgent,
                                QBluetoothServiceInfo,
                                QBluetoothUuid,
                                QLowEnergyService,
                                QLowEnergyCharacteristic)


from ui_service import Ui_ServiceDiscovery

class ServiceDiscoveryDialog(QDialog):
    def __init__(self, deviceInfo, parent=None):
        super().__init__(parent)
        self._ui = Ui_ServiceDiscovery()
        self._ui.setupUi(self)

        self.setWindowTitle(deviceInfo.name())
        
        self._controller = QLowEnergyController()
        self.central = self._controller.createCentral(deviceInfo)
        print("Connecting to device")
        self.central.connectToDevice()
        self.central.connected.connect(self.connected)

        
        # self._serviceDiscovery = QBluetoothServiceDiscoveryAgent(deviceInfo.address())
        # self._serviceDiscovery.serviceDiscovered.connect(self.add_service)

        self._ui.list.itemActivated.connect(self.item_activated)

        self.serviceDic = {}

        self.ServiceSel = 0

        

    def connected(self):
        print("connected to device")
        
        print("Discovering services")
        self.central.discoverServices()
        self.central.serviceDiscovered.connect(self.ServiceDiscovered)
        #self.central.discoveryFinished.connect(self.DiscoveryFinished)

    
    @Slot(QBluetoothUuid)
    def ServiceDiscovered(self,uuid):
        
        service = self.central.createServiceObject(uuid)
        suuidstr = service.serviceUuid().toString()
        sname = service.serviceName()
        
        slabel = f"{suuidstr} {sname}"
        self._ui.list.addItem(slabel)
        print("serviceDiscovered:"+slabel)
        self.serviceDic[suuidstr] = service
        
    @Slot(QListWidgetItem)
    def item_activated(self, item):
        print(item.text()[0:38])
        #{00001800-0000-1000-8000-00805f9b34fb} Generic Access
        #{00001801-0000-1000-8000-00805f9b34fb} Generic Attribute
        #{00001530-1212-efde-1523-785feabcd123} Legacy DFU service
        #{0000180a-0000-1000-8000-00805f9b34fb} Device Information
        #{6e400001-b5a3-f393-e0a9-e50e24dcca9e} nordic uart service
        
        uuid = item.text()[0:38]
        self.ServiceSel = uuid
        service = self.serviceDic[uuid]
        
        mode = QLowEnergyService.DiscoveryMode.FullDiscovery
        service.discoverDetails(mode)
        service.stateChanged.connect(self.StateChanged)

    def StateChanged(self, newState):

        print(newState)
        if newState == QLowEnergyService.ServiceState.RemoteServiceDiscovered:
            print(self.ServiceSel)
            uuid = self.ServiceSel
            service = self.serviceDic[uuid]

            if uuid == '{6e400001-b5a3-f393-e0a9-e50e24dcca9e}':
                print("nordic UART service")
                
                characteristics = service.characteristics()
                #print(characteristics)
                for c in characteristics:
                    #print(c.name())
                    #print(c.value())
                    print(c.uuid())
                    print(c.properties())
                    # c.clientCharacteristicConfiguration()


                    #{6e400003-b5a3-f393-e0a9-e50e24dcca9e} UART TX
                    if c.uuid().toString() == '{6e400003-b5a3-f393-e0a9-e50e24dcca9e}':
                        UartTX = c
                        print('UartTX')
                    #{6e400002-b5a3-f393-e0a9-e50e24dcca9e} UART RX
                    if c.uuid().toString() == '{6e400002-b5a3-f393-e0a9-e50e24dcca9e}':
                        UartRX = c
                        print('UartRX')
                
                #enable notify
                CCCD = UartTX.clientCharacteristicConfiguration()
                data = QByteArray(b'\x01\x00')
                service.writeDescriptor(CCCD,data)

                service.characteristicChanged.connect(self.readUartTX)

                inbyte = QByteArray(b'\x01\x00')
                service.writeCharacteristic(UartRX,inbyte)

                
                

            elif uuid == '{0000180a-0000-1000-8000-00805f9b34fb}':
                print("Device Information service")
                         
                characteristics = service.characteristics()
                for c in characteristics:
                    print(c.name())
                    print(c.value())
                    print(c.properties())
                    # print(c.uuid())
                    # if c.name() == 'Firmware Revision String':
                    #     print(c.value())
                    #     c.characteristicRead.connect(self.CharacteristicRead)

        # else:
        
    
    def readUartTX(self,c,value):
        print('readUartTX')
        print(c.uuid())
        print(value)

