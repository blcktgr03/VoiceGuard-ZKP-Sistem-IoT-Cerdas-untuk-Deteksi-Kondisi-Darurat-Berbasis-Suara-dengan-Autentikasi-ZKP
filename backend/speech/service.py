import logging
import math
import re
import time
import wave
from array import array
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
            transcribe_path = self._normalize_wav_volume(audio_path)
            model = self._get_model()
            logger.info("Running Whisper transcription for %s", transcribe_path)
            started_at = time.perf_counter()
            if self._settings.whisper_engine.strip().lower() == "faster-whisper":
                result = self._transcribe_with_faster_whisper(model, transcribe_path)
            else:
                result = self._transcribe_with_openai_whisper(model, transcribe_path)
            logger.info(
                "%s transcription completed in %.2f seconds using beam_size=%s",
                self.engine_name,
                time.perf_counter() - started_at,
                self._settings.whisper_beam_size,
            )
            text = str(result.get("text", "")).strip()
            if not text or self._looks_like_unusable_transcription(result, text):
                raise SpeechToTextError("Whisper returned an empty transcription.")
            return text
        except SpeechToTextError:
            raise
        except Exception as exc:
            logger.exception("Whisper transcription failed for %s", audio_path)
            raise SpeechToTextError() from exc

    @property
    def engine_name(self) -> str:
        """Return a stable engine label for persisted transcripts."""
        engine = self._settings.whisper_engine.strip().lower()
        if engine == "faster-whisper":
            return f"faster-whisper-{self._settings.whisper_model_name}-{self._settings.whisper_compute_type}"
        return f"openai-whisper-{self._settings.whisper_model_name}"

    def _transcribe_with_faster_whisper(self, model, audio_path: Path) -> dict:
        """Run CTranslate2 Whisper and normalize its segments for shared filtering."""
        segments, _ = model.transcribe(
            str(audio_path),
            language=self._settings.whisper_language or "id",
            task="transcribe",
            beam_size=self._settings.whisper_beam_size,
            temperature=0.0,
            condition_on_previous_text=False,
            initial_prompt=self._settings.whisper_initial_prompt,
            vad_filter=False,
            no_speech_threshold=self._settings.whisper_no_speech_threshold,
            compression_ratio_threshold=3.0,
            log_prob_threshold=-1.5,
        )
        segment_list = list(segments)
        return {
            "text": "".join(segment.text for segment in segment_list),
            "segments": [
                {
                    "no_speech_prob": segment.no_speech_prob,
                    "avg_logprob": segment.avg_logprob,
                    "compression_ratio": segment.compression_ratio,
                }
                for segment in segment_list
            ],
        }

    def _transcribe_with_openai_whisper(self, model, audio_path: Path) -> dict:
        """Run the original PyTorch Whisper implementation as a fallback."""
        options = {
            "language": self._settings.whisper_language or "id",
            "task": "transcribe",
            "temperature": 0.0,
            "condition_on_previous_text": False,
            "fp16": False,
            "no_speech_threshold": self._settings.whisper_no_speech_threshold,
            "compression_ratio_threshold": 3.0,
            "logprob_threshold": -1.5,
        }
        if self._settings.whisper_initial_prompt:
            options["initial_prompt"] = self._settings.whisper_initial_prompt
        if self._settings.whisper_beam_size > 1:
            options["beam_size"] = self._settings.whisper_beam_size
        return model.transcribe(str(audio_path), **options)

    def _get_model(self):
        """Load and cache the configured Whisper model."""
        if self._model is None:
            try:
                if self._settings.whisper_engine.strip().lower() == "faster-whisper":
                    from faster_whisper import WhisperModel

                    model_source = (
                        str(self._settings.whisper_model_path)
                        if self._settings.whisper_model_path
                        else self._settings.whisper_model_name
                    )
                    logger.info(
                        "Loading faster-whisper model '%s' on %s with %s",
                        model_source,
                        self._settings.whisper_device,
                        self._settings.whisper_compute_type,
                    )
                    self._model = WhisperModel(
                        model_source,
                        device=self._settings.whisper_device,
                        compute_type=self._settings.whisper_compute_type,
                    )
                else:
                    import whisper

                    logger.info(
                        "Loading OpenAI Whisper model '%s' on %s",
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

    def warm_up(self) -> None:
        """Load Whisper and run one silent greedy pass during backend startup."""
        try:
            started_at = time.perf_counter()
            model = self._get_model()
            if self._settings.whisper_engine.strip().lower() == "faster-whisper":
                import numpy as np

                segments, _ = model.transcribe(
                    np.zeros(16000, dtype=np.float32),
                    language=self._settings.whisper_language or "id",
                    task="transcribe",
                    beam_size=1,
                    temperature=0.0,
                    condition_on_previous_text=False,
                    vad_filter=False,
                )
                list(segments)
            else:
                import numpy as np

                model.transcribe(
                    np.zeros(16000, dtype=np.float32),
                    language=self._settings.whisper_language or "id",
                    task="transcribe",
                    temperature=0.0,
                    condition_on_previous_text=False,
                    fp16=False,
                )
            logger.info(
                "%s warm-up completed in %.2f seconds.",
                self.engine_name,
                time.perf_counter() - started_at,
            )
        except Exception:
            logger.exception("Whisper warm-up failed; lazy loading remains available.")

    def _normalize_wav_volume(self, audio_path: Path) -> Path:
        """Remove DC offset and normalize INMP441 speech before Whisper."""
        normalized_path = audio_path.with_name(f"{audio_path.stem}_normalized.wav")
        try:
            with wave.open(str(audio_path), "rb") as source:
                channels = source.getnchannels()
                sample_width = source.getsampwidth()
                frame_rate = source.getframerate()
                frame_count = source.getnframes()
                frames = source.readframes(frame_count)

            if channels != 1 or sample_width != 2 or not frames:
                return audio_path

            samples = array("h")
            samples.frombytes(frames)
            if not samples:
                return audio_path

            dc_offset = sum(samples) / len(samples)
            filtered_samples = array("h")
            previous_input = 0.0
            previous_high_pass = 0.0
            previous_low_pass = 0.0
            for sample in samples:
                centered = float(sample) - dc_offset
                # Keep the main speech band: remove low rumble, then soften
                # high-frequency digital noise from the I2S microphone.
                high_passed = centered - previous_input + (0.97 * previous_high_pass)
                filtered = previous_low_pass + (0.82 * (high_passed - previous_low_pass))
                previous_input = centered
                previous_high_pass = high_passed
                previous_low_pass = filtered
                filtered_samples.append(max(-32768, min(32767, int(filtered))))

            activity = self._measure_speech_activity(filtered_samples, frame_rate)
            logger.info(
                "INMP441 activity %s: noise=%.1f p90=%.1f snr_ratio=%.1f active=%.1f%%",
                audio_path,
                activity["noise_floor"],
                activity["p90_level"],
                activity["snr_ratio"],
                activity["active_ratio"] * 100.0,
            )
            if (
                activity["p90_level"] < 140.0
                or activity["snr_ratio"] < 3.0
                or activity["active_ratio"] < 0.10
            ):
                raise SpeechToTextError("INMP441 audio does not contain enough speech activity.")

            peak = max(abs(sample) for sample in filtered_samples)
            if peak == 0:
                return audio_path

            rms = math.sqrt(
                sum(float(sample) * float(sample) for sample in filtered_samples)
                / len(filtered_samples)
            )
            target_rms = 5200.0
            rms_scale = target_rms / max(rms, 1.0)
            peak_scale = 28000.0 / peak
            scale = min(max(rms_scale, 0.35), peak_scale, 12.0)

            for index, sample in enumerate(filtered_samples):
                boosted = int(sample * scale)
                if boosted < -32768:
                    boosted = -32768
                if boosted > 32767:
                    boosted = 32767
                filtered_samples[index] = boosted

            with wave.open(str(normalized_path), "wb") as target:
                target.setnchannels(channels)
                target.setsampwidth(sample_width)
                target.setframerate(frame_rate)
                target.writeframes(filtered_samples.tobytes())

            logger.info(
                "Prepared INMP441 WAV %s: dc=%.1f peak=%s rms=%.1f scale=%.2f",
                audio_path,
                dc_offset,
                peak,
                rms,
                scale,
            )
            return normalized_path
        except SpeechToTextError:
            raise
        except Exception:
            logger.exception("Failed to normalize WAV volume for %s", audio_path)
            return audio_path

    def _measure_speech_activity(self, samples: array, frame_rate: int) -> dict[str, float]:
        """Measure speech-like level changes in 20 ms INMP441 frames."""
        frame_size = max(1, frame_rate // 50)
        frame_levels: list[float] = []
        for start in range(0, len(samples) - frame_size + 1, frame_size):
            frame = samples[start : start + frame_size]
            level = math.sqrt(
                sum(float(sample) * float(sample) for sample in frame) / len(frame)
            )
            frame_levels.append(level)

        if not frame_levels:
            return {
                "noise_floor": 0.0,
                "p90_level": 0.0,
                "snr_ratio": 0.0,
                "active_ratio": 0.0,
            }

        sorted_levels = sorted(frame_levels)
        noise_index = max(0, int(len(sorted_levels) * 0.20) - 1)
        p90_index = min(len(sorted_levels) - 1, int(len(sorted_levels) * 0.90))
        noise_floor = sorted_levels[noise_index]
        p90_level = sorted_levels[p90_index]
        activity_threshold = max(120.0, noise_floor * 3.0)
        active_frames = sum(level > activity_threshold for level in frame_levels)

        return {
            "noise_floor": noise_floor,
            "p90_level": p90_level,
            "snr_ratio": p90_level / max(noise_floor, 1.0),
            "active_ratio": active_frames / len(frame_levels),
        }

    def _looks_like_unusable_transcription(self, result: dict, text: str) -> bool:
        """Reject likely silence/noise hallucinations before they reach BERT."""
        segments = result.get("segments") or []
        if segments:
            no_speech_scores = [
                float(segment.get("no_speech_prob", 0.0))
                for segment in segments
                if segment.get("no_speech_prob") is not None
            ]
            avg_logprobs = [
                float(segment.get("avg_logprob", 0.0))
                for segment in segments
                if segment.get("avg_logprob") is not None
            ]
            compression_ratios = [
                float(segment.get("compression_ratio", 0.0))
                for segment in segments
                if segment.get("compression_ratio") is not None
            ]

            if (
                no_speech_scores
                and min(no_speech_scores) >= 0.92
                and len(text.split()) <= 2
            ):
                return True
            if avg_logprobs and max(avg_logprobs) < -1.5:
                return True
            if compression_ratios and max(compression_ratios) > 3.0:
                return True

        words = re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)
        if len(words) >= 8:
            unique_ratio = len(set(words)) / len(words)
            dominant_count = max(words.count(word) for word in set(words))
            if unique_ratio <= 0.35 or dominant_count >= 4:
                return True

        return False
