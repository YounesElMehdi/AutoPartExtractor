import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, 
    QVBoxLayout, QWidget, QMessageBox, QLabel, QTabWidget, QLineEdit,
    QSpinBox, QFormLayout
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor
from pathlib import Path  # Ensure this is imported

# Import other modules
from app.pdf_processor import extract_text_to_file
from app.utils import (
    create_operation_folder, save_to_file, load_whitelist,
    simple_regex_extractor, levenshtein_similarity,
    load_config, save_config, get_whitelist_path
)

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Regex Pattern
        self.regex_input = QLineEdit(self.config["regex_pattern"])
        layout.addRow("Regex Pattern:", self.regex_input)

        # Similarity Threshold
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(1, 5)
        self.threshold_input.setValue(self.config["similarity_threshold"])
        layout.addRow("Similarity Threshold:", self.threshold_input)

        # Save Button
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.clicked.connect(self.save_settings)
        layout.addRow(self.btn_save)

        self.setLayout(layout)

    def save_settings(self):
        """Save settings to config file."""
        new_config = {
            "regex_pattern": self.regex_input.text(),
            "similarity_threshold": self.threshold_input.value(),
            "whitelist_path": get_whitelist_path()
        }
        save_config(new_config)
        QMessageBox.information(self, "Success", "Settings saved successfully!")

class Worker(QThread):
    progress = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(dict) # Results: {"matched": [], "similar": []}
    error = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.whitelist = load_whitelist()

    def run(self):
        try:
            # Step 1: Create operation folder
            operation_folder = create_operation_folder(self.file_path)
            
            # Step 2: Extract PDF text
            txt_file = operation_folder / "pdftoTxt.txt"
            extract_text_to_file(self.file_path, txt_file)
            self.progress.emit(25)
            
            # Step 3: Regex extraction
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()
            candidates = simple_regex_extractor(text)
            regex_file = operation_folder / "regexExt.txt"
            save_to_file(candidates, regex_file)
            self.progress.emit(50)
            
            # Step 4: Whitelist filtering
            matched = [pn for pn in candidates if pn in self.whitelist]
            not_matched = [pn for pn in candidates if pn not in self.whitelist]
            save_to_file(matched, operation_folder / "MatchWhitelist.txt")
            save_to_file(not_matched, operation_folder / "NotMatchWhitelist.txt")
            self.progress.emit(75)
            
            # Step 5: Similarity check
            similar = {}
            for candidate in not_matched:
                matches = levenshtein_similarity(candidate, self.whitelist)
                if matches:
                    similar[candidate] = matches
            similar_file = operation_folder / "similarPN.txt"
            with open(similar_file, "w", encoding="utf-8") as f:
                for candidate, matches in similar.items():
                    f.write(f"{candidate} → {', '.join(matches)}\n")
            self.progress.emit(100)
            
            # Emit results
            self.finished.emit({
                "matched": matched,
                "similar": similar
            })
            
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()
        self.setWindowTitle("AutoPartExtractor")
        self.setGeometry(100, 100, 800, 600)

    def init_ui(self):
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Main Tab
        main_tab = QWidget()
        self.setup_main_tab(main_tab)
        
        # Settings Tab
        settings_tab = SettingsTab()
        
        self.tabs.addTab(main_tab, "Main")
        self.tabs.addTab(settings_tab, "Settings")
        
        self.setCentralWidget(self.tabs)

    def setup_main_tab(self, tab):
        layout = QVBoxLayout()
        
        # Upload Button
        self.btn_upload = QPushButton("Upload PDF")
        self.btn_upload.clicked.connect(self.upload_pdf)
        
        # Results Display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        
        # Status Label
        self.status_label = QLabel("Ready")
        
        layout.addWidget(self.btn_upload)
        layout.addWidget(self.results_display)
        layout.addWidget(self.status_label)
        
        tab.setLayout(layout)

    def upload_pdf(self):
        """Handles PDF upload and processing."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.results_display.setText(f"Processing: {file_path}...")
            self.status_label.setText("Processing...")
            
            # Disable the button during processing
            self.btn_upload.setEnabled(False)
            
            # Start the worker thread
            self.worker = Worker(file_path)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.on_processing_finished)
            self.worker.error.connect(self.on_processing_error)
            self.worker.start()

    def update_progress(self, value: int):
        """Updates the progress label."""
        self.status_label.setText(f"Processing... {value}%")

    def on_processing_finished(self, results):
        """Updates the UI when processing is complete."""
        self.btn_upload.setEnabled(True)
        self.status_label.setText("Ready")
        
        # Clear previous results
        self.results_display.clear()
        
        # Display matched (green)
        self.results_display.setTextColor(QColor(0, 128, 0))  # Green
        self.results_display.append("Validated Part Numbers:\n" + "\n".join(results["matched"]))
        
        # Display similar (orange)
        self.results_display.setTextColor(QColor(255, 165, 0))  # Orange
        if results["similar"]:
            similar_text = "\n".join(
                [f"{candidate} → {', '.join(matches)}" 
                 for candidate, matches in results["similar"].items()]
            )
            self.results_display.append("\n\nSimilar Part Numbers:\n" + similar_text)
        
        # Reset color
        self.results_display.setTextColor(QColor(0, 0, 0))

    def on_processing_error(self, error_message):
        """Shows an error message if processing fails."""
        self.btn_upload.setEnabled(True)
        self.status_label.setText("Error")
        QMessageBox.critical(self, "Error", f"Failed to process PDF:\n{error_message}")
        self.results_display.setText("Error occurred. Check logs for details.")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()