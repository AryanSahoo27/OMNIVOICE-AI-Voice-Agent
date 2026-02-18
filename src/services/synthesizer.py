import os

class Synthesizer:
    def __init__(self):
        print("✅ Mac Native Mouth Loaded")

    def speak(self, text):
        """
        Uses the built-in macOS 'say' command.
        """
        if not text:
            return
            
        print(f"🗣️  Mac saying: {text}")
        
        # Sanitize text to prevent errors with quotes
        clean_text = text.replace('"', '').replace("'", "")
        
        # 'say' is the native Mac TTS command
        # -r 190 makes it faster (standard conversation speed)
        os.system(f'say -r 190 "{clean_text}"')



