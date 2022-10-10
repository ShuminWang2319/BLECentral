# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Myservice.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QListView, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ServiceDiscovery(object):
    def setupUi(self, ServiceDiscovery):
        if not ServiceDiscovery.objectName():
            ServiceDiscovery.setObjectName(u"ServiceDiscovery")
        ServiceDiscovery.resize(632, 291)
        self.verticalLayout = QVBoxLayout(ServiceDiscovery)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.servicelistView = QListView(ServiceDiscovery)
        self.servicelistView.setObjectName(u"servicelistView")

        self.verticalLayout.addWidget(self.servicelistView)

        self.connect = QPushButton(ServiceDiscovery)
        self.connect.setObjectName(u"connect")

        self.verticalLayout.addWidget(self.connect)

        self.lineEdit = QLineEdit(ServiceDiscovery)
        self.lineEdit.setObjectName(u"lineEdit")

        self.verticalLayout.addWidget(self.lineEdit)

        self.send = QPushButton(ServiceDiscovery)
        self.send.setObjectName(u"send")
        self.send.setAutoDefault(False)
        self.send.setFlat(False)

        self.verticalLayout.addWidget(self.send)

        self.status = QLabel(ServiceDiscovery)
        self.status.setObjectName(u"status")
        self.status.setMouseTracking(False)
        self.status.setTabletTracking(False)

        self.verticalLayout.addWidget(self.status)

        self.buttonBox = QDialogButtonBox(ServiceDiscovery)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ServiceDiscovery)
        self.buttonBox.accepted.connect(ServiceDiscovery.accept)
        self.buttonBox.rejected.connect(ServiceDiscovery.reject)

        self.send.setDefault(False)


        QMetaObject.connectSlotsByName(ServiceDiscovery)
    # setupUi

    def retranslateUi(self, ServiceDiscovery):
        ServiceDiscovery.setWindowTitle(QCoreApplication.translate("ServiceDiscovery", u"Available Services", None))
        self.connect.setText(QCoreApplication.translate("ServiceDiscovery", u"Connect", None))
        self.send.setText(QCoreApplication.translate("ServiceDiscovery", u"Send", None))
        self.status.setText(QCoreApplication.translate("ServiceDiscovery", u"Querying...", None))
    # retranslateUi

