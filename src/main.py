import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import Response
import json, base64, wave, audioop, time, os, asyncio
from dotenv import load_dotenv

from src.services.brain import Brain
from src.services.transcriber import Transcriber as Ears

load_dotenv()

# --- SAFE SETTINGS ---
PORT = 8000
SILENCE_THRESHOLD = 3500   
MAX_SILENCE_CHUNKS = 20 # Standard wait time

app = FastAPI()
brain = Brain()
ears = Ears()

@app.api_route("/{path:path}", methods=["GET", "POST"])
async def catch_all(request: Request, path: str):
    host = request.headers.get('host')
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response><Connect><Stream url="wss://{host}/media-stream" /></Connect></Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Connection Established. Speak naturally.")
    
    audio_buffer = b""
    silence_counter = 0
    is_speaking = False
    
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data['event'] == 'start':
                print(f"🚀 Stream Started")

            elif data['event'] == 'media':
                payload = data['media']['payload']
                chunk = base64.b64decode(payload)
                pcm_chunk = audioop.ulaw2lin(chunk, 2)
                rms = audioop.rms(pcm_chunk, 2)
                
                if rms > SILENCE_THRESHOLD:
                    if not is_speaking:
                        print(f"🎙️  User Speaking...", end="\r")
                        is_speaking = True
                    silence_counter = 0
                    audio_buffer += pcm_chunk
                
                elif is_speaking:
                    audio_buffer += pcm_chunk
                    silence_counter += 1
                    
                    if silence_counter > MAX_SILENCE_CHUNKS:
                        if len(audio_buffer) > 3000: 
                            with wave.open("temp_stream.wav", "wb") as wav_file:
                                wav_file.setnchannels(1); wav_file.setsampwidth(2)
                                wav_file.setframerate(8000); wav_file.writeframes(audio_buffer)
                            
                            user_text = ears.transcribe("temp_stream.wav")
                            
                            if user_text and len(user_text) > 2:
                                t0 = time.perf_counter()
                                print(f"\n🗣️  USER: {user_text}")
                                
                                # Call the "Magic" Brain
                                ai_response = await brain.think(user_text)
                                
                                t1 = time.perf_counter()
                                print(f"🤖 AGENT: {ai_response}")
                                print(f"⚡ Latency: {t1-t0:.3f}s")
                                
                                # Play Audio (Background)
                                clean_msg = ai_response.replace("'", "").replace('"', "")
                                os.system(f"say -v Samantha -r 170 '{clean_msg}' &")
                                
                                if "goodbye" in ai_response.lower():
                                    print("📞 Conversation Finished. Closing connection in 3s...")
                                    await asyncio.sleep(3) # Let the audio finish playing
                                    await websocket.close()
                                    break # Exit the loop
                                print("🎙️  Ready...", end="\r")
                        
                        audio_buffer = b""
                        is_speaking = False
                        silence_counter = 0

            elif data['event'] == 'stop':
                break
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
