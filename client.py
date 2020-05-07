"""Login client"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtNetwork as qtn
from json import dumps
import sys


class client(qtw.QWidget):
    """Client to login to the server"""
    IP = 'xxx.xxx.xxx.xxx'
    PORT = 670

    def __init__(self):
        """Initialize window"""
        super().__init__()

        self.gui()

        self.logbutton.clicked.connect(self.log_in)
        self.sigbutton.clicked.connect(self.new_user)

    def gui(self):
        """create GUI"""

        # widgets
        self.nickname = qtw.QLineEdit()  # nick input
        self.nicknamelabel = qtw.QLabel("Nickname:")
        self.passwd = qtw.QLineEdit()  # password input
        self.passwd.setEchoMode(qtw.QLineEdit.Password)
        self.passwdlabel = qtw.QLabel("Password:")
        self.logbutton = qtw.QPushButton("Log in")
        self.sigbutton = qtw.QPushButton("Sign up")
        self.status = qtw.QTextEdit()

        # four layouts
        self.nicknamelayout = qtw.QHBoxLayout()
        self.passwdlayout = qtw.QHBoxLayout()
        self.buttlayout = qtw.QHBoxLayout()
        self.statuslayout = qtw.QVBoxLayout()

        # adding widgets to nicknamelayout
        self.nicknamelayout.addWidget(self.nicknamelabel)
        self.nicknamelayout.addWidget(self.nickname)

        # adding widgets to passwdlayout
        self.passwdlayout.addWidget(self.passwdlabel)
        self.passwdlayout.addWidget(self.passwd)

        # adding widgets to buttlayout
        self.buttlayout.addWidget(self.logbutton)
        self.buttlayout.addWidget(self.sigbutton)

        # adding widgets to statuslayout
        self.statuslayout.addWidget(self.status)

        # main layout
        self.layout = qtw.QVBoxLayout()

        # adding layouts to the main layout
        self.layout.addLayout(self.nicknamelayout)
        self.layout.addLayout(self.passwdlayout)
        self.layout.addLayout(self.buttlayout)
        self.layout.addLayout(self.statuslayout)

        # setting layout
        self.setLayout(self.layout)

    def log_in(self):
        """Login"""
        self.send_request('log')

    def new_user(self):
        """Registration"""
        self.send_request('new')

    def send_request(self, req_type):
        """Sending request to the server"""
        if not " " in self.passwd.text() and len(self.passwd.text()) > 3:
            self.frame = dumps({'type': req_type, 'nick': self.nickname.text(), 'password': self.passwd.text()})
            self.sock = qtn.QTcpSocket()
            # self.sock.connectToHost(qtn.QHostAddress(self.IP), self.PORT)
            self.sock.connectToHost(qtn.QHostAddress.LocalHost, self.PORT)
            self.sock.write(bytes(self.frame, 'utf8'))
            self.sock.waitForBytesWritten(500)
            self.message()
        else:
            self.status.setText("Password must be longer than 3 letters and must have no spaces. ")

    def message(self):
        """Update status message"""
        try:
            self.sock.waitForReadyRead(250)
            self.mess = str(self.sock.read(4096), 'utf8')
            self.status.setText(self.mess)
        except TypeError:
            self.status.setText("There was an issue with connecting to the server")


if __name__ == "__main__":
    app = qtw.QApplication([])
    cl = client()
    cl.resize(200, 150)
    cl.show()
    sys.exit(app.exec_())
