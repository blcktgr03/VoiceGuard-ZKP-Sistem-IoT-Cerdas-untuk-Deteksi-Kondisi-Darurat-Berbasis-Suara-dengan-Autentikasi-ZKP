class AppError(Exception):
    status_code = 500
    detail = "Application error."

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class AudioProcessingError(AppError):
    status_code = 422
    detail = "Audio could not be processed."


class SpeechToTextError(AppError):
    status_code = 500
    detail = "Speech-to-text pipeline failed."


class ClassificationError(AppError):
    status_code = 500
    detail = "Text classification pipeline failed."


class NotificationError(AppError):
    status_code = 502
    detail = "Notification delivery failed."
