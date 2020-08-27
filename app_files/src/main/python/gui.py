from sys import exit as sysExit
from PyQt5 import sip

from base import context

# Import QApplication and required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QLineEdit, QTextEdit, QLabel, QFrame, QSlider, QDialog, QDialogButtonBox, QGraphicsView
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator


class ErrorDialog(QDialog):
    def __init__(self, title, text):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)
        self.layout = QVBoxLayout()
        self.text = QLabel(text)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.clicked.connect(self.closeEvent)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.done(0)


class StatsBox(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(300)
        self.setFixedWidth(450)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.current_text = "Welcome to the Sudoku Game and Solver!\n\nChoose a board size to begin"
        self.hover_text = "<html style='font-size: 20px;'>This app solves sudoku puzzles using the backtracking algorithm.<br><br>It is a straightforward algorithm that will find a solution to any puzzle (though the most evil puzzles will take a while).<br><br>More information can be found <a style='color: steelblue;' href='https://www.youtube.com/watch?v=JzONv5kaPJM&t=339s'>here</a>.</html>"
        self.setText(self.current_text)
        self.setOpenExternalLinks(True)
        self.setObjectName("stats_box")
        self.setMouseTracking(True)

    def enterEvent(self, e):
        self.current_text = self.text()
        self.setText(self.hover_text)

    def leaveEvent(self, e):
        self.setText(self.current_text)


class SudokuUI(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Sudoku Game and Solver"
        self.width = 800
        self.height = 1000
        self.init_UI()
        valid_characters = QRegExp("[0-9]")
        self.validator = QRegExpValidator(valid_characters, self)

    def keyPressEvent(self, keyEvent):
        super(SudokuUI, self).keyPressEvent(keyEvent)

        if keyEvent.key() == Qt.Key_Q:
            sysExit()

        if keyEvent.key() == Qt.Key_Space:
            self.pause_button.click()

        if keyEvent.key() == Qt.Key_P:
            self.playthrough_button.click()

        if keyEvent.key() == Qt.Key_S:
            self.solve_button.click()

        if keyEvent.key() == Qt.Key_C:
            self.check_button.click()

    def init_UI(self):
        # Set some main window properties
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)
        self.add_stylesheet()
        self.create_main_window()

    def create_error_dialog(self, title, text):
        self.error_dialog = ErrorDialog(title, text)

    def create_main_window(self):
        self.main_window = QMainWindow()

        # Board container
        self.board_container = QFrame()
        self.board_container.setFixedWidth(450)
        self.board_container.setFixedHeight(450)
        self.board_container.setObjectName("board_container")
        # self.board_container.setStyleSheet(self.styles)
        self.grid_layout = QGridLayout()
        self.placeholder_text = QLabel("Select a board size")
        self.placeholder_text.setAlignment(Qt.AlignCenter)
        self.placeholder_text.setObjectName("placeholder_text")
        # self.placeholder_text.setStyleSheet(self.styles)
        self.placeholder_font = self.placeholder_text.font()
        self.placeholder_font.setPointSize(40)
        self.placeholder_text.setFont(self.placeholder_font)
        self.grid_layout.addWidget(self.placeholder_text)
        self.board_container.setLayout(self.grid_layout)

        # Title section
        self.title_section = QWidget()
        self.title_section.setFixedHeight(80)
        self.title_section_layout = QVBoxLayout()
        self.title_section.setLayout(self.title_section_layout)
        self.title = QLabel("Sudoku Game and Solver")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("title")
        # self.title.setStyleSheet(self.styles)
        self.title_section_layout.addWidget(self.title)

        # Board section = board container + board size choice
        self.create_board_size_button_group()
        self.board_section = QWidget()
        self.board_section_layout = QHBoxLayout()
        self.board_section_layout.addWidget(self.board_container)
        self.board_section_layout.addWidget(self.board_size_choice)
        self.board_section_layout.setAlignment(Qt.AlignCenter)
        self.board_section.setLayout(self.board_section_layout)

        # Controls
        self.controls_section = QWidget()
        self.controls_section.setFixedWidth(250)
        self.controls_layout = QVBoxLayout()
        self.controls_section.setLayout(self.controls_layout)

        self.solve_button = QPushButton("Solve (s)", self)
        self.solve_button.setObjectName("button")
        # self.solve_button.setStyleSheet(self.styles)

        self.check_button = QPushButton("Check Solution (c)", self)
        self.check_button.setObjectName("button")
        # self.check_button.setStyleSheet(self.styles)

        self.playthrough_button = QPushButton("Playthrough (p)", self)
        self.playthrough_button.setObjectName("button")
        # self.playthrough_button.setStyleSheet(self.styles)

        self.pause_button = QPushButton("Pause (spacebar)", self)
        self.pause_button.setObjectName("button")
        # self.pause_button.setStyleSheet(self.styles)

        self.quit_button = QPushButton("Quit (q)", self)
        self.quit_button.setObjectName("button")
        # self.quit_button.setStyleSheet(self.styles)

        # Slider text
        self.slider_text = QWidget()
        self.slider_text_layout = QHBoxLayout()
        self.slider_fast = QLabel("Fast")
        self.slider_slow = QLabel("Slow")
        self.slider_slow.setAlignment(Qt.AlignRight)
        self.slider_text_layout.addWidget(self.slider_fast)
        self.slider_text_layout.addWidget(self.slider_slow)
        self.slider_text.setLayout(self.slider_text_layout)
        self.change_speed_slider = QSlider(Qt.Horizontal)
        self.change_speed_slider.setMinimum(1)
        self.change_speed_slider.setMaximum(1000)
        self.change_speed_slider.setValue(1)

        self.solve_button.setDisabled(True)
        self.check_button.setDisabled(True)
        self.playthrough_button.setDisabled(True)

        self.controls_layout.addWidget(self.solve_button)
        self.controls_layout.addWidget(self.check_button)
        self.controls_layout.addWidget(self.playthrough_button)
        self.controls_layout.addWidget(self.slider_text)
        self.controls_layout.addWidget(self.change_speed_slider)
        self.controls_layout.addWidget(self.pause_button)
        self.controls_layout.addWidget(self.quit_button)

        # Stats section
        self.stats_box = StatsBox()
        # self.stats_box.setStyleSheet(self.styles)

        # Bottom section = stats box + controls
        self.bottom_section = QWidget()
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.stats_box)
        self.bottom_layout.addWidget(self.controls_section)
        self.bottom_section.setLayout(self.bottom_layout)

        # Entire app layout
        self.full_app = QVBoxLayout()
        self.full_app.addWidget(self.title_section)  # Top
        self.full_app.addWidget(self.board_section)  # Middle
        self.full_app.addWidget(self.bottom_section)  # Bottom

        self.setLayout(self.full_app)

    def add_stylesheet(self):
        # with open("./styles.css") as file:
        #     self.styles = file.read()
        self.styles = open(context.get_resource("styles/styles.css")).read()
        self.setStyleSheet(self.styles)

    def create_board_size_button_group(self):
        self.board_size_choice = QWidget()
        self.board_size_choice.setFixedWidth(250)
        self.board_size_choice.setFixedHeight(500)
        self.board_sizes = QWidget()

        self.button_layout = QVBoxLayout()

        self.button3 = QPushButton("3x3", self)
        self.button3.setToolTip("Pick a random 3x3 grid")
        self.button3.setObjectName("button")
        # self.button3.setStyleSheet(self.styles)

        self.button4 = QPushButton("4x4", self)
        self.button4.setToolTip("Pick a random 4x4 grid")
        self.button4.setObjectName("button")
        # self.button4.setStyleSheet(self.styles)

        self.button6 = QPushButton("6x6", self)
        self.button6.setToolTip("Pick a random 6x6 grid")
        self.button6.setObjectName("button")
        # self.button6.setStyleSheet(self.styles)

        self.button8 = QPushButton("8x8", self)
        self.button8.setToolTip("Pick a random 8x8 grid")
        self.button8.setObjectName("button")
        # self.button8.setStyleSheet(self.styles)

        self.button9 = QPushButton("9x9", self)
        self.button9.setToolTip("Pick a random 9x9 grid")
        self.button9.setObjectName("button")
        # self.button9.setStyleSheet(self.styles)

        self.add_board_button = QPushButton("Enter custom board", self)
        self.add_board_button.setToolTip(
            "Enter a board of your own for the solver to attempt")
        self.add_board_button.setObjectName("button")
        # self.add_board_button.setStyleSheet(self.styles)
        self.add_board_button.setDisabled(True)

        self.board_size_label = QLabel("Board size:")
        self.board_size_label.setObjectName("board_size_label")
        # self.board_size_label.setStyleSheet(self.styles)
        self.board_size_label.setAlignment(Qt.AlignCenter)

        self.button_layout.addWidget(self.board_size_label)
        self.button_layout.addWidget(self.button3)
        self.button_layout.addWidget(self.button4)
        self.button_layout.addWidget(self.button6)
        self.button_layout.addWidget(self.button8)
        self.button_layout.addWidget(self.button9)
        self.button_layout.addWidget(self.add_board_button)
        self.button_layout.setAlignment(Qt.AlignTop)
        self.button_layout.setSpacing(25)

        self.board_size_choice.setLayout(self.button_layout)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())
        sip.delete(layout)

    def create_grid(self, board_size, starting_board):
        self.clear_layout(self.grid_layout)

        self.grid_layout = QGridLayout()

        for i in range(board_size):
            for j in range(board_size):
                cell = QLineEdit(str(starting_board[i][j]))
                cell.setValidator(self.validator)
                cell.setFixedWidth(400/board_size)
                cell.setFixedHeight(400/board_size)  # MAGIC NUMBERS, FIX THIS
                cell.setAlignment(Qt.AlignCenter)
                cell.setObjectName("empty_cell")
                # cell.setStyleSheet(self.styles)
                if (starting_board[i][j] != 0):
                    cell.setObjectName("prefilled_cell")
                    cell.setEnabled(False)
                cell_font = cell.font()
                cell_font.setPointSize(cell.frameGeometry().width() / 2)
                cell.setFont(cell_font)
                self.grid_layout.addWidget(cell, i, j)

        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.board_container.setLayout(self.grid_layout)
