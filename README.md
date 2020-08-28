# Sudoku Game and Solver

Compiled project, including installable games for macOS, Windows and Linux.

Source code is available in `app_files/src`.

Quick instructions for those who want to build from source:
1. Make sure you have either Python 3.5 or Python 3.6 (>= 3.7 is not yet supported by fbs).
2. Install fbs and PyQt5 with `pip install fbs PyQt5`.
3. Make a new directory where you wish to build the app and `cd` into the directory.
4. Run `fbs startproject` then `fbs run` to make sure the example app runs without issues.
5. Replace the contents of the current `src` directory with those of sudoku_app/app_files/src. This will replace the example app with the source files, styles and resources for the Sudoku app.
6. Feel free to keep the contents as-is, or go crazy with modifications.
7. Once you are happy, bundle the app with `fbs freeze`.
8. After ensuring it works, you can create an installer for your current platform with `fbs installer`. Note, to create a version for another platform, this process must be repeated on that platform.

Full instructions with more detail can be found [here](https://github.com/mherrmann/fbs-tutorial).

(All original source files can be found [here](https://github.com/AkThao/backtrack-sudoku))

Enjoy!
