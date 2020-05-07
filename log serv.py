"""Login sys"""

from cryptography.fernet import Fernet
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtNetwork as qtn
from json import loads
import sys
import json
import mysql.connector


class log_serv(qtw.QPushButton):
    """log_serv"""
    s = 670
    ip = 'xxx.xxx.xxx.xxx'

    def __init__(self):
        """Initialize"""
        super().__init__()
        self.server = qtn.QTcpServer()
        self.sock = qtn.QTcpSocket(self.server)
        # if self.server.listen(qtn.QHostAddress(self.ip), self.s):
        if self.server.listen(qtn.QHostAddress.LocalHost, self.s):
            print(
                f'DATA SERVER:\n\tAddress: {self.server.serverAddress().toString()}\n\tPort: {str(self.server.serverPort())}')
        else:
            print('ERROR!!!!')
            exit()
        self.server.newConnection.connect(self.__session)

        f = open('key.bin', 'rb')

        self.key = f.read()

        f.close()

        self.f = Fernet(self.key)

        del self.key

        # set your properties
        self.db = mysql.connector.connect(
            host = 'localhost',
            user = 'user',
            passwd = 'password',
            database = 'login_data',
            auth_plugin = 'mysql_native_password'
        )

        self.mycursor = self.db.cursor()

    def __session(self):
        """Session"""
        clientconn = self.server.nextPendingConnection()
        clientconn.waitForReadyRead()
        data = str(clientconn.read(4096), 'utf8')
        data = loads(data)
        new = data['type']
        name = data['nick'].lower()
        passwd = data['password']
        # print(new + " " + name + " " + passwd)
        if name.isalnum():
            self.mycursor.execute("SELECT * FROM users WHERE nickname = %s LIMIT 1 ", (name, ))
            temp_db_data = self.mycursor.fetchone()
            if new == 'new':
                if temp_db_data == None:
                    self.mycursor.execute("INSERT INTO users (nickname, password) VALUES (%s, %s)", (name, self.f.encrypt(bytes(passwd, 'utf8'))))
                    self.db.commit()
                    print(name + " - Succesfully signed up")
                    clientconn.write(bytes("Succesfully signed up", 'utf8'))
                    clientconn.waitForBytesWritten()
                else:
                    print(name + " - This user already exists.")
                    clientconn.write(bytes("This user already exists.", 'utf8'))
                    clientconn.waitForBytesWritten()
            elif new == 'log':
                if temp_db_data:
                    localpass = str(self.f.decrypt(bytes(temp_db_data[2], 'utf8')), 'utf8')
                    if localpass == passwd:
                        print(name + " - Succesfully logged in!")
                        clientconn.write(bytes("Succesfully logged in!", 'utf8'))
                        clientconn.waitForBytesWritten()
                    else:
                        clientconn.write(bytes("Login doesn't match with the password", 'utf8'))
                        clientconn.waitForBytesWritten()
                        print(f"Login '{name}' doesn't match with the password")
                else:
                    clientconn.write(bytes("Check your login!", 'utf8'))
                    clientconn.waitForBytesWritten()
                    print(name + " - user not found!")
        else:
            print(name + " - name contains not allowed marks!")
            clientconn.write(bytes('name contains not allowed marks!', 'utf8'))
            clientconn.waitForBytesWritten()

if __name__ == "__main__":
    app = qtw.QApplication([])
    s = log_serv()
    sys.exit(app.exec_())
