import logging
from pathlib import Path

from backend.config.settings import get_settings
from backend.utils.exceptions import SpeechToTextError

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Transcribe audio files with OpenAI Whisper."""

    def __init__(self) -> None:
        """Create a lazy-loading Whisper service."""
        self._settings = get_settings()
        self._model = None

    def transcribe(self, file_path: str) -> str:
        """Transcribe an audio file into text."""
        audio_path = Path(file_path)
        if not audio_path.exists():
            raise SpeechToTextError(f"Audio file does not exist: {file_path}")

        try:
            model = self._get_model()
            options = {}
            if self._settings.whisper_language:
                options["language"] = self._settings.whisper_language

            logger.info("Running Whisper transcription for %s", audio_path)
            result = model.transcribe(str(audio_path), **options)
            text = str(result.get("text", "")).strip()
            if not text:
                raise SpeechToTextError("Whisper returned an empty transcription.")
            return text
        except SpeechToTextError:
            raise
        except Exception as exc:
            logger.exception("Whisper transcription failed for %s", audio_path)
            raise SpeechToTextError() from exc

    def _get_model(self):
        """Load and cache the configured Whisper model."""
        if self._model is None:
            try:
                import whisper

                logger.info(
                    "Loading Whisper model '%s' on %s",
                    self._settings.whisper_model_name,
                    self._settings.whisper_device,
                )
                self._model = whisper.load_model(
                    self._settings.whisper_model_name,
                    device=self._settings.whisper_device,
                )
            except Exception as exc:
                logger.exception("Failed to load Whisper model.")
                raise SpeechToTextError() from exc
        return self._model
