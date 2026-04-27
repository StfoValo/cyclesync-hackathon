from PyQt6.QtCore import QObject, QThread, pyqtSignal
import random

# --- IMPORT THE NEW ORCHESTRATOR INSTEAD OF THE OLD AGENT ---
from mcp_agent_server.ai_orchestrator import AIOrchestrator

# --- The Streaming Background Thread ---
class AgentWorker(QThread):
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, sector, quantity, value):
        super().__init__()
        self.sector = sector
        self.quantity = quantity
        self.value = value
        
        # Initialize the new scalable orchestrator
        self.agent = AIOrchestrator()

    def run(self):
        # Point to the specific Recycler route we created!
        for chunk in self.agent.run_recycler_analysis(self.sector, self.quantity, self.value):
            self.chunk_received.emit(chunk)
            QThread.msleep(30) 
        self.finished.emit()

# --- The Controller ---
class AnalyticsController(QObject):
    def __init__(self, hub_view, market_model):
        super().__init__()
        self.hub = hub_view
        self.market_model = market_model
        
        self.hub.analytics.back_requested.connect(self.show_exchange)
        self.bind_exchange_buttons()

    def bind_exchange_buttons(self):
        market_data = self.market_model.get_market_overview()
        self.hub.exchange.render_market_cards(market_data)
        
        for i in range(self.hub.exchange.flowLayout.count()):
            card = self.hub.exchange.flowLayout.itemAt(i).widget()
            if card:
                btn = card.layout().itemAt(card.layout().count() - 1).widget()
                row_data = market_data[i]
                btn.clicked.connect(lambda checked, data=row_data: self.launch_analysis(data))

    def show_exchange(self):
        self.hub.stacked_widget.setCurrentIndex(0)

    def launch_analysis(self, row_data):
        self.hub.stacked_widget.setCurrentIndex(1)
        
        sector = row_data['material_sector']
        quantity = row_data['quantity_tons']
        value = row_data['estimated_salvage_value_eur']
        mock_market_price = (value / quantity) * random.uniform(1.1, 1.4)
        
        self.hub.analytics.populate_data(sector, quantity, value, mock_market_price)
        
        self.current_markdown = "" 
        self.hub.analytics.ai_terminal.setMarkdown("> Establishing secure connection to Enterprise AI Core...")
        
        self.worker = AgentWorker(sector, quantity, value)
        self.worker.chunk_received.connect(self.on_chunk_received)
        self.worker.finished.connect(self.on_agent_finished)
        self.worker.start()

    def on_chunk_received(self, chunk):
        self.current_markdown += chunk
        self.hub.analytics.ai_terminal.setMarkdown(self.current_markdown)
        
        scrollbar = self.hub.analytics.ai_terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_agent_finished(self):
        self.hub.analytics.btn_action.show()