"""
dashboard/api_client.py
---------------------------
Camada fina que isola todas as chamadas HTTP ao servidor MonitorPro,
para que o resto do dashboard (as telas PySide6) não precise saber
nada sobre requests/JSON — só chama métodos como `api.list_computers()`.
"""

import requests


class ApiClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.token: str | None = None

    def _headers(self) -> dict:
        """Monta o header de autenticação, se já houver um token de login salvo."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def login(self, username: str, password: str) -> None:
        """Autentica no servidor e guarda o token JWT para as próximas chamadas."""
        response = requests.post(
            f"{self.server_url}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def get_branding(self) -> dict:
        response = requests.get(f"{self.server_url}/branding", timeout=10)
        response.raise_for_status()
        return response.json()

    def list_computers(self) -> list[dict]:
        response = requests.get(
            f"{self.server_url}/computers", headers=self._headers(), timeout=10
        )
        response.raise_for_status()
        return response.json()

    def get_computer_metrics(self, computer_id: int) -> list[dict]:
        response = requests.get(
            f"{self.server_url}/computers/{computer_id}/metrics",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def list_blocked_domains(self) -> list[dict]:
        response = requests.get(f"{self.server_url}/domains", timeout=10)
        response.raise_for_status()
        return response.json()

    def add_blocked_domain(self, domain: str) -> dict:
        response = requests.post(
            f"{self.server_url}/domains",
            json={"domain": domain},
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def remove_blocked_domain(self, domain_id: int) -> None:
        response = requests.delete(
            f"{self.server_url}/domains/{domain_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
