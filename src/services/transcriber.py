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
            return self._correct_jargon(text)
        except Exception as e:
            print(f"❌ Transcription Error: {e}")
            return ""

    def _correct_jargon(self, text):
        lower_text = text.lower()
       # Add these to your replacements dictionary
        replacements = {
            "to be": "2-bedroom",
            "tree be": "3-bedroom",
            "man hat an": "Manhattan",
            "brook lin": "Brooklyn",
            "million": "Million",
            "penthouse": "Penthouse",
            "brown stone": "Brownstone" 
        }
        
        for wrong, right in replacements.items():
            if wrong in lower_text:
                text = text.replace(wrong, right)
                text = text.replace(wrong.title(), right)
        return text