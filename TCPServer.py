import sys,os, re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
# 整数校验器 
intValidator = QIntValidator() 
# # 添加错误日志记录 # 全局使用[cgitb]来捕获异常信息,界面不要突然退出！ 
# tracelogDir = './tracelog' # 
# if not os.path.exists(tracelogDir): os.makedirs(tracelogDir) 
# import cgitb 
# # cgitb.enable( # logdir=tracelogDir, # display=False, # context=5, # format='text', # ) 
def robust(actual_do):
    def add_robust(*args, **keyargs):
        try:
            return actual_do(*args, **keyargs)
        except Exception as e:
            print ('Error execute: %s \nException: %s' % (actual_do.__name__, e))
            return add_robust
        
class Serverapp(QMainWindow):
    def __init__(self ) -> None:
        super().__init__()
        self.resize(400,400)
        self.setWindowTitle('TCPServer')
        self.setStyleSheet('* {font-family: Microsoft YaHei;font-size:14px;} QTextBrowser{ font-size:12px;}')
        self.setui()
    def setui(self):
        #初始化状态条和菜单
        self.initStatusBar()
        self.localIP = self.getLocalIP() # 获取本机ip 
        # 设置公共布局的节点信息
        self.commonInputIP = QLineEdit(self.localIP)
        self.commonInputPort = QLineEdit('5555')
        self.commonInputPort.setValidator(intValidator)
        self.commonInputPort.setStyleSheet('max-width:60px')
        self.logBrowser = QTextBrowser()
        # 设置server_布局1
        serverGrid = QGridLayout()
        serverGrid.addWidget(QLabel('设置IP/PORT'),1,1)
        serverGrid.addWidget(self.commonInputIP,1,2)
        serverGrid.addWidget(self.commonInputPort,1,3)
        self.openServerBtn = QPushButton('侦听', clicked=self.Toggle_Server_clicked)
        serverGrid.addWidget(self.openServerBtn, 1,4)
        serverGrid.addWidget(QLabel('日志记录'),2,1)
        serverGrid.addWidget(self.logBrowser,2,2,1,3)
        serverGrid.addWidget(QPushButton('testBtn', clicked=self.testBtnClicked), 4,1)
        self.send_browser = QTextEdit() 
        serverGrid.addWidget(self.send_browser, 4,2,1,3)
        self.initServerParams()
        # add_layout 
        mainFrame = QWidget()
        mainFrame.setLayout(serverGrid)
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
        self.statusBar.showMessage('在线人数:0') # 初始化服务端的参数 

    def initServerParams(self): 
        self._isServerOpen=False 
        self.clientsMap={} 
    @pyqtSlot() 
    def Toggle_Server_clicked(self): 
        if self._isServerOpen: 
            self.serverServer.close() 
            self._isServerOpen=False 
            self.openServerBtn.setText('侦听') 
            # 停止监听，服务器将不再监听传入的连接，并不是停止接收数据 
            # #调用_deleteLater_不立即销毁对象，向主消息循环发送了一个event，
            # 下一次主消息循环收到这个event之后才会销毁对象 
            self.serverServer.deleteLater() 
            self.logBrowser.append("close_server, end") 
        else: 
            self.serverServer = QTcpServer() 
            sportState = self.serverServer.listen(QHostAddress(self.commonInputIP.text()), int(self.commonInputPort.text())) 
            if not sportState: return QMessageBox.critical(self, '严重错误', '打开失败,请检查是否已经被占用！') 
            self.serverServer.newConnection.connect(self.on_server_newConnection) 
            self.logBrowser.append("open_server, begin") 
            self._isServerOpen=True 
            self.openServerBtn.setText('断开') 
    def on_server_newConnection(self): 
        self.serverSocket = self.serverServer.nextPendingConnection() 
        # 获取客户端的IP端口等信息 
        uuid='{}_{}'.format(self.serverSocket.peerAddress().toString(), self.serverSocket.peerPort()) 
        self.clientsMap[uuid]=self.serverSocket 
        self.logBrowser.append('Connected with: {} success!'.format(uuid)) 
        self.statusBar.showMessage('在线人数:{}'.format(len(self.clientsMap))) 
        # 接收信息和断开连接的信号槽方法 
        self.serverSocket.readyRead.connect(lambda: self.on_socket_readyRead(uuid)) 
        self.serverSocket.disconnected.connect(lambda: self.disconnected_slot(uuid)) 
    def disconnected_slot(self, addr): 
        removeItem = self.clientsMap.pop(addr) 
        removeItem.close() 
        self.statusBar.showMessage('在线人数:{}'.format(len(self.clientsMap))) 
        self.logBrowser.append('Disconnected with: {}!'.format(addr)) 
        # @pyqtSlot() @robust 
    def on_socket_readyRead(self, addr): 
        inblock = self.clientsMap[addr].readAll() 
        print(addr, 'inblock_:{}'.format(inblock)) 
        strblock = str(inblock, encoding='utf-8') 
        self.logBrowser.append("fromAddr_:{}, tx: {}, msg: {}".format(addr, len(inblock), strblock)) 
        self.sendCount += len(inblock) 
        self.receiveCount += len(inblock) 
        self.globalStatus.setText('S: {}, R: {}'.format(self.sendCount, self.receiveCount)) 
        # 广播消息给所有连接的客户端,除了自己 
        for senderAddr in self.clientsMap: 
            if senderAddr!=addr: 
                client=self.clientsMap[senderAddr] 
                client.write(inblock) 
    def testBtnClicked(self): 
        msg='hello-yy3,time:{}'.format(QDateTime.currentDateTime().toString('hh:mm:ss')) 
        msg = self.send_browser.toPlainText() 
        self.sendCount += len(msg) 
        self.globalStatus.setText('S: {}, R: {}'.format(self.sendCount, self.receiveCount)) 
        for senderAddr in self.clientsMap: 
            if senderAddr!='': 
                client=self.clientsMap[senderAddr] 
                client.write(msg.encode("utf-8")) 
    def getLocalIP(self):
        '''获取本地主机IP''' 
        for addr in QNetworkInterface.allAddresses(): 
            # 只要IPv4地址，过滤掉127.0.0.1 
            if addr.protocol() == QAbstractSocket.NetworkLayerProtocol.IPv4Protocol and addr != QHostAddress.SpecialAddress.LocalHost: 
                address = addr.toString() 
                # 169开头的IP地址表示本地主机未从DHCP分配到有效IP，过滤网关地址x.x.x.1 
                if address[:3] != '169' and address.split('.')[-1] != '1': 
                    return address 
                return '0.0.0.0' 
            # 关闭窗口前的处理方法 
    def closeEvent(self, event): 
        if self._isServerOpen: 
            self.serverServer.close() 
            self._isServerOpen=False 
            self.openServerBtn.setText('侦听') 
            # 停止监听，服务器将不再监听传入的连接，并不是停止接收数据 
            # #调用_deleteLater_不立即销毁对象，向主消息循环发送了一个event，
            # 下一次主消息循环收到这个event之后才会销毁对象 
            self.serverServer.deleteLater() 
            print('=======================close_server: {}!======================='.format(QDateTime.currentDateTime().toString('hh:mm:ss'))) 
                
if __name__ == "__main__": 
    app = QApplication([]) 
    server_app = Serverapp() 
    server_app.show() 
    app.exec_()




