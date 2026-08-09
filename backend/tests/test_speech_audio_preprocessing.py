import math
import wave
from array import array

import pytest

from backend.speech.service import SpeechToTextService
from backend.utils.exceptions import SpeechToTextError


def test_speech_activity_separates_speech_from_silence() -> None:
    service = SpeechToTextService()
    silence = array("h", [25] * 16000)
    speech = array(
        "h",
        [
            int(1200 * math.sin(2 * math.pi * 220 * index / 16000))
            if 3200 <= index < 12800
            else 25
            for index in range(16000)
        ],
    )

    silent_activity = service._measure_speech_activity(silence, 16000)
    speech_activity = service._measure_speech_activity(speech, 16000)

    assert silent_activity["active_ratio"] == 0.0
    assert speech_activity["active_ratio"] >= 0.5
    assert speech_activity["p90_level"] > 140.0


def test_quiet_inmp441_wav_is_rejected_before_whisper(tmp_path) -> None:
    service = SpeechToTextService()
    audio_path = tmp_path / "quiet.wav"
    with wave.open(str(audio_path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(16000)
        target.writeframes(array("h", [20] * 64000).tobytes())

    with pytest.raises(SpeechToTextError):
        service._normalize_wav_volume(audio_path)
