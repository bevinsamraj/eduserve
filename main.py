import sys
from gui.login import LoginWindow
from dash_app import DashboardWindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    login = LoginWindow()
    if login.exec_() == 1:  # If login success
        user_info = login.get_user()
        dashboard = DashboardWindow(user_info)
        dashboard.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__ == "__main__":
    main()
