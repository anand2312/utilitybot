class ContentNotFoundError(ValueError):
    """Error raised when a specific query could not be found."""


class BadContentTypeError(ValueError):
    """Error raised when the inputted content type is invalid."""
