class MKMSZRError(Exception):
    """Base exception for the patching core."""


class RomValidationError(MKMSZRError):
    """Raised when an input ROM is not the supported clean image."""


class PatchError(MKMSZRError):
    """Raised when a guarded patch site does not match the expected bytes."""
