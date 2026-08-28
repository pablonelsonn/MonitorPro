"""
dashboard/login_window.py
-----------------------------
Primeira tela exibida ao abrir o dashboard: pede usuário/senha e,
se a autenticação funcionar, abre a MainWindow.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

from dashboard.api_client import ApiClient
from dashboard.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self, api: ApiClient, brand_name: str):
        super().__init__()
        self.api = api
        self.main_window: MainWindow | None = None  # mantém referência viva após o login

        self.setWindowTitle(f"{brand_name} - Login")
        self.setFixedSize(320, 180)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<h2>{brand_name}</h2>"))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuário")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Entrar")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        # Permite apertar Enter no campo de senha para logar, sem precisar clicar no botão.
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha usuário e senha.")
            return

        try:
            self.api.login(username, password)
        except Exception as exc:
            QMessageBox.critical(self, "Falha no login", f"Não foi possível entrar: {exc}")
            return

        self.main_window = MainWindow(self.api)
        self.main_window.show()
        self.close()
