from faster_whisper import WhisperModel
import os

class Transcriber:
    def __init__(self):
        model_size = "base.en"
        print(f"Loading Faster-Whisper model: {model_size}...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("✅ Faster-Whisper Model Loaded.")

    def transcribe(self, audio_path):
    try:
        segments, info = self.model.transcribe(audio_path, beam_size=5, language='en')
        text = " ".join([segment.text for segment in segments]).strip()
        return text  # Returned directly without passing to another function
    except Exception as e:
        print(f"❌ Transcription Error: {e}")
        return ""
