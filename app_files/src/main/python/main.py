from base import context
from PyQt5.QtWidgets import QMainWindow

import gui
import solve_sudoku_recursive
import boards
from sys import exit as sysExit
import random
import time

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QObject


class SudokuCtrl:
    def __init__(self, view, model):
        # Set up the app by adding the view and model to the GUI
        self._view = view
        self._solver = model

        # Animation variables
        self.animation_speed = 1
        self.temp_board_states = []
        self.is_animating = False
        self.step_count = 0

        # Import all boards and set up all controls
        self._create_boards_lists()
        self._connect_signals()

    def _create_boards_lists(self):
        """Copy the file containing all the boards into a dictionary, where key = board_size"""
        self.boards_lists = {
            3: boards.boards_3,
            4: boards.boards_4,
            6: boards.boards_6,
            8: boards.boards_8,
            9: boards.boards_9
        }

    def pick_random_board(self, board_size):
        """Choose a random board of a specified size and set the controls appropriately"""
        self.board_size = board_size
        self.board_data = self.boards_lists[self.board_size]
        self.board = random.choice(self.board_data[0])
        self._view.create_grid(self.board_size, self.board)
        self._view.solve_button.setDisabled(False)
        self._view.check_button.setDisabled(False)
        self._view.playthrough_button.setDisabled(False)
        self._view.change_speed_slider.setDisabled(False)
        self._view.add_board_button.setDisabled(False)
        self._view.pause_button.setText("Pause (spacebar)")
        self._view.pause_button.repaint()
        self._view.pause_button.clicked.disconnect()
        self._view.pause_button.clicked.connect(self.pause_animation)
        self._view.add_board_button.setText("Enter custom board")
        self._view.add_board_button.repaint()
        self._view.add_board_button.clicked.disconnect()
        self._view.add_board_button.clicked.connect(self.input_custom_board)
        self.temp_board_states = []
        self.get_empty_cells()
        self.display_new_board_stats()
        self.step_count = 0

    # Set of functions to update the stats box based on the current state of the app
    def display_new_board_stats(self):
        self._view.stats_box.current_text = f"New board\n\nBoard size: {self.board_size}\nNumber of empty cells: {len(self.empty_cells)}"
        self._view.stats_box.setText(self._view.stats_box.current_text)
        self._view.stats_box.repaint()

    def display_solved_stats(self, time):
        self._view.stats_box.current_text = f"Time taken to solve puzzle: {str(time*1000)[:5]} ms\n\nNumber of steps taken: {self.num_states}\n\nNumber of backtracks: {self.num_backtracks}"
        self._view.stats_box.setText(self._view.stats_box.current_text)
        self._view.stats_box.repaint()

    def display_check_stats(self, correct, incorrect):
        self._view.stats_box.current_text = f"Cells correct: {correct}\n\nCells incorrect: {incorrect}\n\nScore: {correct/(correct+incorrect)*100:.1f}%"
        self._view.stats_box.setText(self._view.stats_box.current_text)
        self._view.stats_box.repaint()

    def display_playthrough_stats(self):
        self._view.stats_box.current_text = f"Current step: {self.step_count}\n\nNumber of backtracks: {self.num_backtracks}"
        self._view.stats_box.setText(self._view.stats_box.current_text)
        self._view.stats_box.repaint()

    def display_input_custom_board_stats(self):
        self._view.stats_box.current_text = f"New board of size {self.board_size}x{self.board_size}\n\nEnter values for a puzzle of your own then click \"Done\" to have the solver attempt to solve the puzzle."
        self._view.stats_box.setText(self._view.stats_box.current_text)
        self._view.stats_box.repaint()

    def display_currently_solving_stats(self):
        self._view.stats_box.current_text = "Running animation..."
        self._view.stats_box.setText(self._view.stats_box.current_text)
        self._view.repaint()

    def display_invalid_board_stats(self, error_message):
        self._view.stats_box.current_text = f"<html>Invalid board, could not be solved.<br><br><b>{error_message}.</b><br><br>Please check that all input values satisfy the rules of Sudoku.</html>"
        self._view.stats_box.setText(self._view.stats_box.current_text)
        self._view.stats_box.repaint()

    def input_custom_board(self):
        """Present the user with an empty board and accept their own input for a new puzzle"""
        self.board = [[0] * self.board_size for i in range(self.board_size)]
        self._view.create_grid(self.board_size, self.board)
        self._view.solve_button.setDisabled(True)
        self._view.check_button.setDisabled(True)
        self._view.playthrough_button.setDisabled(True)
        self.display_input_custom_board_stats()
        self.empty_cells = []

        self._view.add_board_button.setText("Done")
        self._view.add_board_button.repaint()
        self._view.add_board_button.clicked.disconnect()
        self._view.add_board_button.clicked.connect(self.test_custom_board)

    def test_custom_board(self):
        """Attempt to solve the board given by the user, use the stats box to indicate whether or not the board is valid"""
        # First check for unfilled cells, every cell must contain a number, even if they are all zeroes
        if (self.check_for_unfilled_cells()):
            self._view.create_error_dialog(
                "Empty Cell Error", "Cannot test board, it has unfilled cells.\n\nPlease fill in all cells to continue.\nCells to be solved should contain a zero.")
            self._view.error_dialog.exec_()
            return

        # Read the board input and store it locally
        self.get_current_board_state()
        self.board = self.current_board_state
        self.get_empty_cells()

        # Validate the board using a function from the solver file
        # is_board_valid can take two forms:
        # For valid boards, it will be: is_board_valid = (True, "No error")
        # For invalid board, it will take the form: is_board_valid = (False, ERROR_CODE, row, col)
        # where row and col represent the problem cell
        is_board_valid = self._solver.validate_board(board=self.board,
                                                     board_size=self.board_size,
                                                     subgrid_height=self.board_data[2],
                                                     subgrid_width=self.board_data[3])

        if is_board_valid[0]:
            # Solve the board and display the result, along with the relevant stats
            self._view.create_grid(self.board_size, self.board)
            self.show_answer()
            self._view.add_board_button.setText("Enter custom board")
            self._view.add_board_button.repaint()
            self._view.add_board_button.clicked.disconnect()
            self._view.add_board_button.clicked.connect(
                self.input_custom_board)

        else:
            # Display the error message to the user and highlight the problem cell
            # User can keep trying or move on and use a built-in puzzle
            error_message = is_board_valid[1]
            incorrect_cell = (is_board_valid[2], is_board_valid[3])
            self.display_invalid_board_stats(error_message)
            for i in range(self.board_size):
                for j in range(self.board_size):
                    self.change_cell_style(i, j, "empty_cell")
            self.change_cell_style(
                incorrect_cell[0], incorrect_cell[1], "incorrect_cell")

    def solve_puzzle(self):
        """Call the backtrack algorithm and store the result as a member variable"""
        self.result = self._solver.main(BOARD=self.board,
                                        board_size=self.board_size,
                                        subgrid_height=self.board_data[2],
                                        subgrid_width=self.board_data[3])

    def show_answer(self):
        """Solve the current puzzle and display the solution with animation"""
        start = time.time()
        self.solve_puzzle()
        end = time.time()
        time_taken = end - start
        self.get_board_states()
        self._view.button3.setDisabled(True)
        self._view.button4.setDisabled(True)
        self._view.button6.setDisabled(True)
        self._view.button8.setDisabled(True)
        self._view.button9.setDisabled(True)
        self._view.add_board_button.setDisabled(True)
        self._view.solve_button.setDisabled(True)
        self._view.check_button.setDisabled(True)
        self._view.playthrough_button.setDisabled(True)
        self._view.pause_button.setDisabled(True)
        self.display_currently_solving_stats()
        QApplication.processEvents()
        for cell in self.empty_cells:
            self.update_cell(cell[0], cell[1], str(
                self.result[cell[0]][cell[1]]))
            self.change_cell_style(cell[0], cell[1], "solved_cell")
            QApplication.processEvents()
            QThread.msleep(self.animation_speed)
        self.count_backtracks()
        self.display_solved_stats(
            time_taken)
        self.num_backtracks = 0

        self._view.button3.setDisabled(False)
        self._view.button4.setDisabled(False)
        self._view.button6.setDisabled(False)
        self._view.button8.setDisabled(False)
        self._view.button9.setDisabled(False)
        self._view.add_board_button.setDisabled(False)
        self._view.playthrough_button.setDisabled(False)
        self._view.pause_button.setDisabled(False)

    def update_cell(self, row, col, value):
        """Update cell at [row, col] to show 'value'"""
        self._view.grid_layout.itemAtPosition(row, col).widget().setText(value)
        self._view.grid_layout.itemAtPosition(
            row, col).widget().setEnabled(False)

    def change_cell_style(self, row, col, cell_style):
        """Change a cell's CSS based on its state (solved, correct, incorrect, empty....)"""
        # Setting object name allows style to be applied
        self._view.grid_layout.itemAtPosition(
            row, col).widget().setObjectName(cell_style)
        self._view.grid_layout.itemAtPosition(
            row, col).widget().setStyleSheet(self._view.styles)
        # Repaint is necessary as board won't show the new style otherwise
        self._view.grid_layout.itemAtPosition(row, col).widget().repaint()

    def get_cell(self, row, col):
        """Return the value of cell at [row, col]"""
        return int(self._view.grid_layout.itemAtPosition(row, col).widget().text())

    def get_current_board_state(self):
        """Store a 2D array of the current board state"""
        self.current_board_state = []

        for i in range(self.board_size):
            self.current_board_state.append([])
            for j in range(self.board_size):
                self.current_board_state[i].append(self.get_cell(i, j))

    def check_for_unfilled_cells(self):
        """Scan the entire board and check if there are any cells not containing a number"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                if str(self._view.grid_layout.itemAtPosition(i, j).widget().text()) == "":
                    return True
        return False

    def check_answer(self):
        """Compare user's input to solution and colour-code cells to show correct/incorrect values"""
        if (self.check_for_unfilled_cells()):
            self._view.create_error_dialog(
                "Empty Cell Error", "Cannot check solution, board has unfilled cells.\n\nPlease fill in all cells to continue.\nIf you are stuck, feel free to input random numbers.")
            self._view.error_dialog.exec_()
            return
        self.get_current_board_state()
        self.solve_puzzle()

        # No need to check twice
        self._view.solve_button.setDisabled(True)
        self._view.check_button.setDisabled(True)

        correct, incorrect = 0, 0

        for cell in self.empty_cells:
            self._view.grid_layout.itemAtPosition(
                cell[0], cell[1]).widget().setEnabled(False)
            if (self.result[cell[0]][cell[1]] == self.current_board_state[cell[0]][cell[1]]):
                self.change_cell_style(cell[0], cell[1], "correct_cell")
                correct += 1
            else:
                self.change_cell_style(cell[0], cell[1], "incorrect_cell")
                incorrect += 1

        self.display_check_stats(correct, incorrect)
        self._view.solve_button.setDisabled(False)

    def get_board_states(self):
        """Retrieve current puzzle's solution, saved in a list by solver"""
        self.board_states = []
        self.board_states = self._solver.get_board_states()

        self.num_states = len(self.board_states)

    def is_backtrack(self, prev_state, new_state):
        """Return True or False depending on whether or not the algorithm has backtracked"""
        prev_num_zeroes = sum(row.count(0) for row in prev_state)
        new_num_zeroes = sum(row.count(0) for row in new_state)

        # If there are more zeroes now than before, it means the algorithm has backtracked
        return (new_num_zeroes > prev_num_zeroes)

    def count_backtracks(self):
        """Count the number of backtracks required to solve a puzzle"""
        self.num_backtracks = 0
        for i in range(1, len(self.board_states)):
            self.num_backtracks += self.is_backtrack(
                self.board_states[i-1], self.board_states[i])

    def run_animation(self, reset_count):
        """Display animation of solving algorithm on board"""
        # Pressing these buttons during the animation can crash the app, so just disable them
        if (self.check_for_unfilled_cells()):
            self._view.create_error_dialog(
                "Empty Cell Error", "Cannot run playthrough, board has unfilled cells.\n\nThe playthrough algorithm reads the numbers in the board,\nso every cell in the board must contain a number.\nPlease fill in all cells to continue.")
            self._view.error_dialog.exec_()
            return
        self._view.solve_button.setDisabled(True)
        self._view.check_button.setDisabled(True)
        self._view.button3.setDisabled(True)
        self._view.button4.setDisabled(True)
        self._view.button6.setDisabled(True)
        self._view.button8.setDisabled(True)
        self._view.button9.setDisabled(True)
        self._view.add_board_button.setDisabled(True)

        # Chosen to disable the slider during animation for now
        # Because animation and slider both run on main thread
        # So slider cannot update until main event loop progresses
        # Not an issue for fast animation, but on slow animation (e.g. 1s sleep), this wait time becomes obvious
        self._view.change_speed_slider.setDisabled(
            True)  # TEMPORARY, FIX IN FUTURE (multithreading)

        if reset_count:
            self.step_count, self.num_backtracks = 0, 0
            self.current_board_state = self.board
        # Used to control pausing/resuming of the animation
        self.is_animating = True

        self._view.pause_button.setText("Pause (spacebar)")
        self._view.pause_button.repaint()
        self._view.pause_button.clicked.disconnect()
        self._view.pause_button.clicked.connect(self.pause_animation)
        QApplication.processEvents()
        while len(self.board_states) > 0:
            new_state = self.board_states[0]
            del self.board_states[0]
            for cell in self.empty_cells:
                previous_cell_value = self.get_cell(cell[0], cell[1])
                new_cell_value = new_state[cell[0]][cell[1]]
                self.update_cell(cell[0], cell[1], str(
                    new_state[cell[0]][cell[1]]))
                if new_cell_value == 0:
                    self.change_cell_style(cell[0], cell[1], "incorrect_cell")
                elif new_cell_value == previous_cell_value:
                    self.change_cell_style(cell[0], cell[1], "solved_cell")
                else:
                    self.change_cell_style(cell[0], cell[1], "correct_cell")
            self.step_count += 1
            self.num_backtracks += self.is_backtrack(
                self.current_board_state, new_state)
            self.display_playthrough_stats()
            self.get_current_board_state()
            # Return control to main event loop to display updated board
            QApplication.processEvents()
            # self.animation_speed is a delay between "frames"
            QThread.msleep(self.animation_speed)

        # Show that every cell is correct when animation has completed but not when paused
        if self.is_animating:
            for cell in self.empty_cells:
                self.change_cell_style(cell[0], cell[1], "correct_cell")

        # Re-enable buttons now that animation has finished
        self._view.button3.setDisabled(False)
        self._view.button4.setDisabled(False)
        self._view.button6.setDisabled(False)
        self._view.button8.setDisabled(False)
        self._view.button9.setDisabled(False)
        self._view.add_board_button.setDisabled(False)
        self._view.change_speed_slider.setDisabled(False)
        self._view.solve_button.setDisabled(False)
        self.is_animating = False

    def pause_animation(self):
        """Pause the backtrack algorithm solving animation"""
        if self.is_animating:
            self.is_animating = False
            self._view.change_speed_slider.setDisabled(False)
            self._view.solve_button.setDisabled(False)
            # The animation is "paused" by emptying the board_states list so the while loop in self.run_animation stops
            self.temp_board_states, self.board_states = self.board_states, []
            self.current_num_backtracks = self.num_backtracks
            # Change the pause button to a continue button
            self._view.pause_button.setText("Continue (spacebar)")
            self._view.pause_button.repaint()
            self._view.pause_button.clicked.disconnect()
            self._view.pause_button.clicked.connect(self.continue_animation)
            QApplication.processEvents()
        else:
            # Can't pause something that isn't running
            self._view.create_error_dialog(
                "Playthrough Error", "Playthrough not running.\n\nNothing to pause.")
            self._view.error_dialog.exec_()

    def continue_animation(self):
        """Resume the backtrack algorithm solving animation"""
        # Don't need to set self.is_animating = True, as this is done in self.run_animation
        self._view.change_speed_slider.setDisabled(True)
        self._view.solve_button.setDisabled(True)
        # Refill the board_states list and "resume" the while loop in self.run_animation from where it left off
        self.board_states = self.temp_board_states
        self.num_backtracks = self.current_num_backtracks
        # Change the continue button to a pause button
        self._view.pause_button.setText("Pause (spacebar)")
        self._view.pause_button.repaint()
        self._view.pause_button.clicked.disconnect()
        self._view.pause_button.clicked.connect(self.pause_animation)
        self.is_animating = True
        QApplication.processEvents()
        self.run_animation(reset_count=False)

    def change_speed(self):
        """Update the animation speed to the new value on the slider"""
        self.animation_speed = self._view.change_speed_slider.value()

    def get_empty_cells(self):
        """Store a list of empty_cell coordinates, we almost never need to deal with prefilled cells"""
        self.empty_cells = self._solver.return_list_of_empty_cells(self.board)

    def quit(self):
        """Call sys.exit()"""
        sysExit()

    def _connect_signals(self):
        """Set up controller interface by connecting signals from GUI components to relevant slots"""
        self._view.button3.clicked.connect(lambda: self.pick_random_board(3))
        self._view.button4.clicked.connect(lambda: self.pick_random_board(4))
        self._view.button6.clicked.connect(lambda: self.pick_random_board(6))
        self._view.button8.clicked.connect(lambda: self.pick_random_board(8))
        self._view.button9.clicked.connect(lambda: self.pick_random_board(9))
        self._view.add_board_button.clicked.connect(self.input_custom_board)

        self._view.solve_button.clicked.connect(self.show_answer)
        self._view.check_button.clicked.connect(self.check_answer)
        # Multiple successive connect statements for the same signal connect that signal to all specified slots
        self._view.playthrough_button.clicked.connect(self.solve_puzzle)
        self._view.playthrough_button.clicked.connect(self.get_board_states)
        self._view.playthrough_button.clicked.connect(
            lambda: self.run_animation(True))
        self._view.pause_button.clicked.connect(self.pause_animation)
        self._view.quit_button.clicked.connect(self.quit)
        self._view.change_speed_slider.valueChanged.connect(self.change_speed)



def main():
    view = gui.SudokuUI()
    view.show()
    model = solve_sudoku_recursive
    SudokuCtrl(view=view, model=model)
    exit_code = context.app.exec_()
    sysExit(exit_code)


if __name__ == '__main__':
    main()
