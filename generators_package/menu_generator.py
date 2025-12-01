"""Menu generator."""

# -- Imports --

from typing import Dict, Callable, Any


class Menu:
    """Menu generator.

    ## Description
    Base class for menus.
    ## Attributes
    ```
    self.name: str # Menu name
    self.current_selection: int # Stores the index to the currently selected option
    self.options: Dict[Callable[[], str], Callable[..., Any]] # Stores the options
    ```
    ## Methods
    ```
    get_option(self, index: int) -> Callable[..., Any] # Return the option located at index `index`.
    get_labels(self) -> list[str] # Return the current label text for each option.
    ```
    """

    def __init__(
        self,
        options: Dict[Callable[[], str], Callable[..., Any]],
        name: str = "",
        current_selection: int = 0,
    ) -> None:
        """Initilise menu."""
        self.name: str = name
        self.current_selection: int = current_selection
        self.options: Dict[Callable[[], str], Callable[..., Any]] = options

    def get_option(self, index: int) -> Callable[..., Any]:
        """Return the option located at index `index`."""
        counter = 0
        for option in list(self.options.keys()):
            if counter == index:
                return self.options[option]
            counter += 1
        raise NotImplementedError

    def get_labels(self) -> list[str]:
        """Return the current label text for each option."""
        return [label_func() for label_func in self.options.keys()]
