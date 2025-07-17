from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QMessageBox
import sqlite3, bcrypt

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduSense Login")
        self.setFixedSize(350, 250)
        layout = QVBoxLayout()
        self.email = QLineEdit(); self.email.setPlaceholderText("Email")
        self.passwd = QLineEdit(); self.passwd.setPlaceholderText("Password"); self.passwd.setEchoMode(QLineEdit.Password)
        self.role = QComboBox(); self.role.addItems(["Teacher","Student","Admin"])
        login_btn = QPushButton("Login")
        reg_btn = QPushButton("Register")
        login_btn.clicked.connect(self.login)
        reg_btn.clicked.connect(self.register)
        layout.addWidget(QLabel("EduSense Login")); layout.addWidget(self.email)
        layout.addWidget(self.passwd); layout.addWidget(self.role)
        layout.addWidget(login_btn); layout.addWidget(reg_btn)
        self.setLayout(layout)
        self.user = None
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect("./data/users.db")
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )""")
        self.conn.commit()
    
    def login(self):
        email = self.email.text()
        pw = self.passwd.text()
        role = self.role.currentText()
        c = self.conn.cursor()
        c.execute("SELECT password, role FROM users WHERE email=?", (email,))
        res = c.fetchone()
        if res and bcrypt.checkpw(pw.encode(), res[0].encode()) and res[1]==role:
            self.user = {"email": email, "role": role}
            self.accept()
        else:
            QMessageBox.warning(self, "Login failed", "Incorrect credentials or role.")
    
    def register(self):
        email = self.email.text()
        pw = self.passwd.text()
        role = self.role.currentText()
        c = self.conn.cursor()
        c.execute("SELECT email FROM users WHERE email=?", (email,))
        if c.fetchone():
            QMessageBox.warning(self, "Register", "Email already registered!")
            return
        h_pw = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (email,password,role) VALUES (?,?,?)", (email, h_pw, role))
        self.conn.commit()
        QMessageBox.information(self, "Registered", "Registration successful. You can login now.")
    
    def get_user(self):
        return self.user
