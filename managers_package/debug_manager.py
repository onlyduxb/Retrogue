"""Debug manager."""

# -- Imports --

import inspect
import os.path
from datetime import datetime
from typing import Any


def get_caller_file():
    """Return the file name of the caller of the debugger."""
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    caller_filename_full = frame.f_code.co_filename  # type: ignore
    return os.path.splitext(os.path.basename(caller_filename_full))[0]


def get_caller_class():
    """Return the name of the class that called the debugger."""
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    locals_ = frame.f_locals  # type: ignore

    if "self" in locals_:
        return locals_["self"].__class__.__name__

    if "cls" in locals_:
        return locals_["cls"].__name__

    return None


def get_caller_function():
    """Return the name of the function that called the debugger."""
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    return frame.f_code.co_name  # type: ignore


class Debugger:
    """Debugger.

    ## Description
    Creates a log file with the filename being the provided argument
    ## Attributes
    ```
    self.on: bool # If debugger is not wanated set to true
    self.file_path = f"{file_name}.log" # File path
    self.percist: bool # Set to true if you wanzt logs to save after re-running (False by default)
    ```
    ## Methods
    ```
    write(self, message) # Writes a single line into the log file created by the current object
    write_map(self, map: list[list[Any]]) # Writes an itterable into the log file
    ```
    """

    def __init__(self, file_name: str, percist=False, dud=False) -> None:
        """Initalise debugger."""
        self.on = True  # Enable / disable debugger
        self.file_path = f"{file_name}.log"  # File path
        self.percist = percist  # Set to true if you want logs to save after re-running (False by default)
        with open(self.file_path, "a" if self.percist else "w"):
            pass

    def write(self, message):
        """Write a single line into the log file created by the current object."""
        if self.on:
            message = str(message)  # Strings the message
            with open(self.file_path, "a") as file:
                file.write(
                    f'[{datetime.now().strftime("%H:%M:%S.%f")[:-3]}] [{get_caller_file()}/{get_caller_class()}/{get_caller_function()}] {message} \n'
                )
            file.close()

    def write_map(self, map: list[list[Any]]):
        """Write a map row by row into the log file created by the current object (end of map is marked by '-----------')."""
        with open(self.file_path, "a") as file:
            for row in map:
                file.write(f"{row} \n")
            file.write("----------- \n")
        file.close()
