import os
import sys
import subprocess
import concurrent.futures
from dotenv import load_dotenv
from sarvamai import SarvamAI
from groq import Groq

load_dotenv()

def split_audio_ffmpeg(audio_path, output_dir, segment_time=28):
    """Splits long audio into small segments using ffmpeg."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Clear directory if it exists
    for f in os.listdir(output_dir):
        if f.startswith("segment_"):
            os.remove(os.path.join(output_dir, f))

    segment_pattern = os.path.join(output_dir, "segment_%03d.mp3")
    
    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-f", "segment",
        "-segment_time", str(segment_time),
        "-c", "copy",
        segment_pattern
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    segments = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.startswith("segment_")])
    return segments

def transcribe_chunk(api_key, chunk_path):
    """Transcribes a single <30s chunk via Sarvam API."""
    try:
        client = SarvamAI(api_subscription_key=api_key)
        with open(chunk_path, "rb") as f:
            response = client.speech_to_text.transcribe(
                file=f,
                model="saaras:v3",
                mode="transcribe"
            )
        return getattr(response, 'transcript', str(response)).strip()
    except Exception as e:
        print(f"\n[Warning] Chunk {os.path.basename(chunk_path)} failed: {e}")
        return ""

def generate_mom(audio_path: str, output_dir: str = None):
    if not os.path.exists(audio_path):
        print(f"❌ Error: File '{audio_path}' not found.")
        return

    sarvam_key = os.getenv("SARVAM_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if not sarvam_key or not groq_key:
        print("❌ Error: Missing API keys in .env")
        return

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    temp_dir = os.path.join(os.path.dirname(audio_path) or ".", f"temp_{base_name}")

    print(f"✂️  Splitting audio into chunks...")
    try:
        chunks = split_audio_ffmpeg(audio_path, temp_dir)
        num_chunks = len(chunks)
        print(f"🎙️ Transcribing {num_chunks} chunks in parallel with Sarvam AI...")

        results = [""] * num_chunks
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_idx = {executor.submit(transcribe_chunk, sarvam_key, chunk): i for i, chunk in enumerate(chunks)}
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()
                sys.stdout.write("█")
                sys.stdout.flush()
        
        full_transcript = " ".join([r for r in results if r]).strip()
        print("\n✅ Transcription complete.")

    except Exception as e:
        print(f"\n❌ Transcription failed: {e}")
        return
    finally:
        # Cleanup temporary audio chunks
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

    if not full_transcript:
        print("❌ No speech detected.")
        return

    print("🧠 Generating MoM with Groq...")
    groq_client = Groq(api_key=groq_key)
    prompt = f"""
    You are an expert consultant for Uncensored Runtime. Read the following conversational transcript and provide a structured Minutes of Meeting (MoM) summary.
    
    Include strictly:
    1. Main Topic/Objective
    2. Key Points Discussed
    3. Decisions Made or Action Items (if applicable)
    
    (Do not use markdown formatting like * or **. Format in plain text).
    
    Transcript:
    {full_transcript}
    """

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        mom_text = completion.choices[0].message.content.strip()

        # --- UPDATED SAVING LOGIC ---
        if output_dir is None:
            output_dir = os.path.dirname(audio_path) or "."
        else:
            os.makedirs(output_dir, exist_ok=True) # Creates the new folder if it doesn't exist

        output_file = os.path.join(output_dir, f"{base_name}_mom.txt")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(mom_text)

        print(f"🎉 MoM successfully saved to: {output_file}")
        print("\n--- MINUTES OF MEETING ---\n")
        print(mom_text)
        print("\n--------------------------")

    except Exception as e:
        print(f"❌ MoM Generation failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.module_b_mom <path_to_audio_file>")
        sys.exit(1)
        
    generate_mom(sys.argv[1])
