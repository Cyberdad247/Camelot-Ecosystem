"""BaseKnight - Abstract base for all Camelot knights."""

from abc import ABC, abstractmethod


class BaseKnight(ABC):
    name: str = "Unknown Knight"
    title: str = "Knight"
    specialty: str = "General"
    icon: str = "[K]"

    @abstractmethod
    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        """Execute a directive.

        Args:
            directive: The raw user directive string.
            intent: Compiled intent dict from Anya (keys: intent, domain,
                    complexity, tokens, runic, cartridge).
            write: If True, write generated files to disk.

        Returns:
            dict with keys: status ("success"|"error"), output (str),
            files_created (list of file paths).
        """
        pass

    def format_header(self) -> str:
        return f"{self.icon} {self.name} ({self.title}) -- {self.specialty}"
