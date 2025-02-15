from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoPartExtractor")
        self.setGeometry(100, 100, 800, 600)
        
        # Create widgets
        self.btn_upload = QPushButton("Upload PDF", self)
        self.results_display = QTextEdit(self)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.btn_upload)
        layout.addWidget(self.results_display)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Connect button
        self.btn_upload.clicked.connect(self.upload_pdf)
    
    def upload_pdf(self):
        """Handles PDF upload."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.results_display.setText(f"Processing: {file_path}...")
            # Add your processing logic here later