class ValidationException(Exception):
    """Parent class for validation exception."""

    pass


class DirectoryException(ValidationException):
    pass


class ImageException(ValidationException):
    pass


class LabelException(ValidationException):
    pass


class YamlException(ValidationException):
    pass


class DatatypeException(ValidationException):
    pass


class JsonException(ValidationException):
    pass


class Id2LabelJsonException(ValidationException):
    pass