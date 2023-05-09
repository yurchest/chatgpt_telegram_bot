class CustomRateLimitError(Exception):
    """
        Exception raised RateLimitError.
    """

    def __init__(self, message="RateLimitError"):
        self.message = message
        super().__init__(self.message)
