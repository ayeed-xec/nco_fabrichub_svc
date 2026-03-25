class NdfcProviderError(Exception):
    """Raised when a provider probe/action fails."""

    def __init__(self, message: str, endpoint: str, critical: bool = True):
        super().__init__(message)
        self.endpoint = endpoint
        self.critical = critical
