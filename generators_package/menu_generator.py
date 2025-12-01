"""Menu generator."""

# -- Imports --

from typing import Dict, Callable, Any

class Menu:
    """Menu generator.

    ## Description
    ## Attributes
    ## Methods
    """

    def __init__(self, options, name='', current_selection=0) -> None:
        """Initilise menu."""
        self.name=name
        self.current_selection=current_selection
        self.options: Dict[Callable[[], str], Callable[..., Any]] = options

    def get_option(self, index: int):
        """Return the option located at index `index`."""
        counter=0
        for option in list(self.options.keys()):
            if counter==index:
                return self.options[option]
            counter+=1
        raise NotImplementedError

    def get_labels(self):
        """Return the current label text for each option."""
        return [label_func() for label_func in self.options.keys()]