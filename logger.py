from PyQt5.QtWidgets import QTextEdit


class UiLogger:
    def __init__(self) -> None:
        super().__init__()
        self.console_output = None

    def init_ui_console(self, widget):
        self.console_output = QTextEdit(widget)
        self.console_output.setReadOnly(True)

    def print(self, text="", sep=' ', end='\n', file=None):
        print(text, sep=sep, end=end, file=file)
        self.console_output.append(f"{text}{end}")


logger = UiLogger()
