"""Domain and transport exceptions for Portal Imóveis MG research."""


class PortalMGException(Exception):
    """Base exception for all Portal Imóveis MG operations."""


class PropertyNotFoundException(PortalMGException):
    """Raised when a requested property listing is not found."""


class NetworkTransportException(PortalMGException):
    """Raised when an HTTP communication failure occurs."""


class ParsingException(PortalMGException):
    """Raised when server response payload fails to parse."""


class ValidationException(PortalMGException):
    """Raised when input criteria fails domain validation."""
