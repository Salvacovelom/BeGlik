class CustomException(Exception):
    message = "An unknown error occurred."
    status_code = 500
    errors = []

    def __init__(self, message=None, status_code=None, errors=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        if errors:
            self.errors = errors
    
    def __str__(self):
        return f"{self.message} - {self.errors}"
