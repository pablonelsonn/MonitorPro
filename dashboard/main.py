"""
dashboard/main.py
---------------------
Ponto de entrada do painel administrativo (PySide6).

Para rodar: python dashboard/main.py
Ajuste SERVER_URL para o endereço real do servidor MonitorPro.
"""

import os
import sys

from PySide6.QtWidgets import QApplication

from dashboard.api_client import ApiClient
from dashboard.login_window import LoginWindow

SERVER_URL = os.environ.get("MONITORPRO_SERVER_URL", "http://localhost:8000")


def main() -> None:
    app = QApplication(sys.argv)

    api = ApiClient(SERVER_URL)

    # Busca o nome de marca configurado no servidor para exibir na tela de login.
    # Se o servidor estiver fora do ar, cai no nome padrão "MonitorPro".
    try:
        brand_name = api.get_branding()["brand_name"]
    except Exception:
        brand_name = "MonitorPro"

    login_window = LoginWindow(api, brand_name)
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
