"""
dashboard/main_window.py
----------------------------
Janela principal do dashboard, exibida após o login. Tem duas abas:

- "Computadores": lista as máquinas monitoradas, status online/offline
  e uso atual de CPU/RAM/disco.
- "Domínios bloqueados": permite adicionar/remover domínios da lista
  de bloqueio administrativo.

Um QTimer atualiza a lista de computadores automaticamente a cada
10 segundos, para o administrador ver o status em tempo quase-real
sem precisar apertar F5.
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox,
    QHeaderView,
)

from dashboard.api_client import ApiClient

REFRESH_INTERVAL_MS = 10_000  # 10 segundos


class MainWindow(QMainWindow):
    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api

        self.setWindowTitle("MonitorPro - Painel Administrativo")
        self.resize(900, 600)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        tabs.addTab(self._build_computers_tab(), "Computadores")
        tabs.addTab(self._build_domains_tab(), "Domínios bloqueados")

        # Timer de atualização automática da lista de computadores.
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_computers)
        self.refresh_timer.start(REFRESH_INTERVAL_MS)

        # Primeira carga imediata, sem esperar o primeiro tick do timer.
        self.refresh_computers()
        self.refresh_domains()

    # ---------- Aba: Computadores ----------

    def _build_computers_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.computers_table = QTableWidget(0, 5)
        self.computers_table.setHorizontalHeaderLabels(
            ["Hostname", "Status", "CPU", "RAM", "Disco"]
        )
        self.computers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.computers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.computers_table)

        return widget

    def refresh_computers(self) -> None:
        """Busca a lista atualizada de computadores no servidor e repopula a tabela."""
        try:
            computers = self.api.list_computers()
        except Exception as exc:
            print(f"[Dashboard] Falha ao atualizar computadores: {exc}")
            return

        self.computers_table.setRowCount(len(computers))
        for row, computer in enumerate(computers):
            status = "🟢 Online" if computer["is_online"] else "🔴 Offline"

            # Métricas mais recentes exigiriam outra chamada por computador;
            # aqui mostramos hostname/status, e o detalhamento de CPU/RAM/disco
            # fica disponível ao dar duplo-clique (ver get_computer_metrics).
            self.computers_table.setItem(row, 0, QTableWidgetItem(computer["hostname"]))
            self.computers_table.setItem(row, 1, QTableWidgetItem(status))
            self.computers_table.setItem(row, 2, QTableWidgetItem("—"))
            self.computers_table.setItem(row, 3, QTableWidgetItem("—"))
            self.computers_table.setItem(row, 4, QTableWidgetItem("—"))

            # Ao carregar métricas reais sob demanda (evita N chamadas a cada refresh automático):
            self._fill_latest_metrics(row, computer["id"])

    def _fill_latest_metrics(self, row: int, computer_id: int) -> None:
        """Busca a métrica mais recente de um computador e preenche as colunas de CPU/RAM/disco."""
        try:
            metrics = self.api.get_computer_metrics(computer_id)
        except Exception:
            return
        if not metrics:
            return
        latest = metrics[0]
        self.computers_table.setItem(row, 2, QTableWidgetItem(f"{latest['cpu_percent']:.0f}%"))
        self.computers_table.setItem(row, 3, QTableWidgetItem(f"{latest['ram_percent']:.0f}%"))
        self.computers_table.setItem(row, 4, QTableWidgetItem(f"{latest['disk_percent']:.0f}%"))

    # ---------- Aba: Domínios bloqueados ----------

    def _build_domains_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.domains_table = QTableWidget(0, 2)
        self.domains_table.setHorizontalHeaderLabels(["Domínio", "Ação"])
        self.domains_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.domains_table)

        add_row = QHBoxLayout()
        self.new_domain_input = QLineEdit()
        self.new_domain_input.setPlaceholderText("ex.: facebook.com")
        add_row.addWidget(self.new_domain_input)

        add_button = QPushButton("Bloquear domínio")
        add_button.clicked.connect(self.handle_add_domain)
        add_row.addWidget(add_button)

        layout.addLayout(add_row)

        return widget

    def refresh_domains(self) -> None:
        try:
            domains = self.api.list_blocked_domains()
        except Exception as exc:
            print(f"[Dashboard] Falha ao atualizar domínios: {exc}")
            return

        self.domains_table.setRowCount(len(domains))
        for row, domain in enumerate(domains):
            self.domains_table.setItem(row, 0, QTableWidgetItem(domain["domain"]))

            remove_button = QPushButton("Remover")
            remove_button.clicked.connect(lambda _, d=domain: self.handle_remove_domain(d))
            self.domains_table.setCellWidget(row, 1, remove_button)

    def handle_add_domain(self) -> None:
        domain = self.new_domain_input.text().strip()
        if not domain:
            return
        try:
            self.api.add_blocked_domain(domain)
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Não foi possível bloquear o domínio: {exc}")
            return
        self.new_domain_input.clear()
        self.refresh_domains()

    def handle_remove_domain(self, domain: dict) -> None:
        try:
            self.api.remove_blocked_domain(domain["id"])
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Não foi possível remover o domínio: {exc}")
            return
        self.refresh_domains()
