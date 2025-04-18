from PyQt5.QtWidgets import * 
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtNetwork import * 
import os, shutil, re 
import socket 
# 整数校验器 
intValidator = QIntValidator() 
# 添加错误日志记录 # 全局使用[cgitb]来捕获异常信息,界面不要突然退出！ 
# tracelogDir = './tracelog' # 
# if not os.path.exists(tracelogDir): os.makedirs(tracelogDir) # 
# import cgitb 
# cgitb.enable( # logdir=tracelogDir, # display=False, # context=5, # format='text', # ) 
def robust(actual_do): 
    def add_robust(*args, **keyargs): 
        try: 
            return actual_do(*args, **keyargs) 
        except Exception as e: 
            print ('Error execute: %s \nException: %s' % (actual_do.__name__, e)) 
            return add_robust 

class Clientapp(QMainWindow): 
    def __init__(self ) -> None: 
        super().__init__() 
        self.resize(400,400) 
        self.setWindowTitle('TCPClient') 
        self.setStyleSheet('* {font-family: Microsoft YaHei;font-size:14px;} QTextBrowser{ font-size:12px;}') 
        self.setui() 
    def setui(self): 
        #初始化状态条和菜单 
        self.initStatusBar() 
        self.localIP = self.getLocalIP() 
        # 获取本机ip 
        # # 设置公共布局的节点信息 
        # # 设置client_布局 
        clientGrid = QGridLayout() 
        clientGrid.addWidget(QLabel('设置IP/PORT'),1,1) 
        self.commonInputIP = QLineEdit(self.localIP) 
        self.commonInputPort = QLineEdit('5555') 
        self.commonInputPort.setValidator(intValidator) 
        self.commonInputPort.setStyleSheet('max-width:60px') 
        clientGrid.addWidget(self.commonInputIP,1,2) 
        clientGrid.addWidget(self.commonInputPort,1,3) 
        self.toggleBtn = QPushButton('连接', clicked=self.Toggle_Button_clicked) 
        clientGrid.addWidget(self.toggleBtn, 1,4) 
        clientGrid.addWidget(QLabel('日志记录'), 2,1) 
        self.logBrowser = QTextBrowser() 
        clientGrid.addWidget(self.logBrowser, 2,2,1,3) 
        clientGrid.addWidget(QPushButton('testBtn', clicked=self.testBtnClicked), 3,1) 
        self.send_browser = QTextEdit() 
        clientGrid.addWidget(self.send_browser, 3,2,1,3) 
        self.initClientParams() 
        # add_layout 
        mainFrame = QWidget() 
        mainFrame.setLayout(clientGrid) 
        self.setCentralWidget(mainFrame) 
    
    def initStatusBar(self): 
        self.statusBar = QStatusBar(self) 
        #添加一个显示永久信息的标签控件 
        self.sendCount=0 
        self.receiveCount=0 
        self.globalStatus = QLabel('S: {}, R: {}'.format(self.sendCount, self.receiveCount)) 
        self.globalStatus.setAlignment(Qt.AlignRight) 
        self.statusBar.addPermanentWidget(self.globalStatus) 
        self.setStatusBar(self.statusBar) 
        self.statusBar.showMessage('未连接') 
    
    # 客户端方法 
    def initClientParams(self): 
        self._isOpen=False 
        self.connectState=0 
    
    #客户端初始的连接状态 
    def Toggle_Button_clicked(self): 
        if self._isOpen: 
            self.clientSocket.disconnectFromHost() 
        else: 
            # 开始设置发送文件数据的客户端，并连接到服务端 
            try: 
                self.clientSocket = QTcpSocket() 
                self.clientSocket.connectToHost(self.commonInputIP.text(), int(self.commonInputPort.text()) ) 
                self.clientSocket.stateChanged.connect(self.stateChangedTrigger) 
                self.clientSocket.readyRead.connect(self.on_socket_readyRead) 
            except Exception as e: 
                QMessageBox.critical(self, '严重错误', '设置客户端失败: {}'.format(e)) 
                
    def on_socket_readyRead(self): 
        cdatablock = self.clientSocket.readAll() # 
        # strblock = cdatablock.decode('utf-8') 
        strblock = str(cdatablock, encoding='utf-8') 
        self.logBrowser.append(strblock) 
        print('cdatablock_:', cdatablock) 
        self.receiveCount += len(cdatablock) 
        self.globalStatus.setText('S: {}, R: {}'.format(self.sendCount, self.receiveCount)) 
        
    def testBtnClicked(self): 
        # msg='hello-yy3,time:{}'.format(QDateTime.currentDateTime().toString('hh:mm:ss')) 
        msg = self.send_browser.toPlainText() 
        self.clientSocket.write(msg.encode("utf-8")) 
        self.sendCount += len(msg) 
        self.globalStatus.setText('S: {}, R: {}'.format(self.sendCount, self.receiveCount)) 
        
    def stateChangedTrigger(self, currentstate): 
        print('===ConnectState:{}==='.format(currentstate)) 
        self.connectState=currentstate
        #QAbstractSocket.ConnectedState【3】, QAbstractSocket.UnconnectedState【0】 
        if currentstate==QAbstractSocket.ConnectedState: 
            self.statusBar.showMessage('Connected!') 
            self.logBrowser.append('Connected to server success!') 
            self.toggleBtn.setText('断开') 
            self._isOpen=True 
        else: 
            self.statusBar.showMessage('Disconnected!') 
            self.logBrowser.append('Disconnected with server!') 
            self.toggleBtn.setText('连接') 
            self._isOpen=False

    def getLocalIP(self): 
        # '''获取本地主机IP''' 
        for addr in QNetworkInterface.allAddresses(): 
            if addr.protocol() == QAbstractSocket.NetworkLayerProtocol.IPv4Protocol and addr != QHostAddress.SpecialAddress.LocalHost: 
                address = addr.toString() 
                if address[:3] != '169' and address.split('.')[-1] != '1': 
                    return address 
                return '0.0.0.0' 
            
    def closeEvent(self, event): 
        if self._isOpen: 
            self.clientSocket.disconnectFromHost() 
            print('=======================close_Client: {}!======================='.format(QDateTime.currentDateTime().toString('hh:mm:ss'))) 
                
if __name__ == "__main__": 
    app = QApplication([]) 
    client_app = Clientapp() 
    client_app.show() 
    app.exec_()




