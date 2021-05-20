"""Handles the database interactions for storing notes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    user: int
    content: str
