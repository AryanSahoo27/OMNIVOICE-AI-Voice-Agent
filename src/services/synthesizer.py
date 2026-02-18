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



# import os
# import wave
# import time
# import piper

# class Synthesizer:
#     def __init__(self):
#         self.model_path = "src/services/amy.onnx"
#         self.voice = None

#         if not os.path.exists(self.model_path):
#             print(f"❌ ERROR: Model not found at {self.model_path}")
#         else:
#             print(f"⬇️  Loading Piper Model: {self.model_path}...")
#             self.voice = piper.PiperVoice.load(self.model_path)
#             print("✅ Piper Mouth Loaded")

#     def speak(self, text):
#         if not self.voice:
#             return

#         print(f"🗣️  Piper saying: {text}")
#         start = time.time()
#         output_file = "temp_speech.wav"

#         try:
#             with wave.open(output_file, 'wb') as wav_file:
#                 # --- THE FIX: Set parameters BEFORE writing ---
#                 wav_file.setnchannels(1)                # Mono
#                 wav_file.setsampwidth(2)                # 16-bit audio
#                 wav_file.setframerate(self.voice.config.sample_rate) # Get rate from model
                
#                 # Now it is safe to write
#                 self.voice.synthesize(text, wav_file)
            
#             # Play using Mac native player
#             os.system(f"afplay {output_file}")
            
#             print(f"   (Spoke in {time.time() - start:.2f}s)")

#         except Exception as e:
#             print(f"❌ Error speaking: {e}")

# if __name__ == "__main__":
#     mouth = Synthesizer()
#     mouth.speak("System initialized. The channel configuration is now correct.")