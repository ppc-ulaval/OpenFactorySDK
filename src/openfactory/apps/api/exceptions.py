class APIException(Exception):
    """Base exception for API errors"""
    pass

class DeviceNotFoundException(APIException):
    """Raised when a device is not found"""
    pass

class StreamCreationException(APIException):
    """Raised when stream creation fails"""
    pass