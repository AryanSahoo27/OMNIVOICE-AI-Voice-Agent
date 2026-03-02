import os
import google.generativeai as genai
import asyncio
from dotenv import load_dotenv

load_dotenv()

class Brain:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return

        genai.configure(api_key=api_key) 
        self.model_name = 'models/gemini-flash-latest' 
        
        self.system_instruction = (
            "You are OmniVoice, a Senior Property Consultant for ATS Global NYC. "
            "Goal: Collect Name, Area (Manhattan/Brooklyn), Budget (Millions), and Unit Type.\n"
            
            "CLOSING PROTOCOL:\n"
            "Once you have all 4 details (Name, Area, Budget, Unit Type), you MUST conclude the call. "
            "Say EXACTLY: 'I have logged your requirements, [Name]. Our Senior Partner will contact you shortly to schedule a private viewing. Goodbye!'\n\n"

            """
KNOWLEDGE BASE:
- MANHATTAN: 
    * Tribeca/SoHo: High-end lofts and penthouses. Median ~$3.5M.
    * Upper East Side: Classic pre-war opulence and brownstones.
    * Hudson Yards: Ultra-modern glass skyscrapers and condos.
- BROOKLYN: 
    * DUMBO: Iconic waterfront condos with Manhattan views.
    * Park Slope: Famous for historic, leafy brownstones.
    * Williamsburg: Trendy, modern condos and converted industrial spaces.

CONVERSATIONAL UPGRADE:
- Use this knowledge to validate the user. 
- Example: If they say 'Brooklyn', say 'Excellent, Brooklyn Heights and DUMBO have some incredible waterfront options right now.'
- Example: If they say '$4 Million', say 'A $4 million budget is perfect for a classic brownstone in Park Slope or a modern loft in Tribeca.'
"""
            "INTELLIGENT PARDON RULES:\n"
            "1. If a user says something that sounds like 'Manhattan' (e.g., 'Valentine', 'Mountain', 'Man') or 'Brooklyn' (e.g., 'Broken', 'Lin'), "
            "assume they meant the location and say: 'I believe you mentioned [Manhattan/Brooklyn], is that correct?' and move to the next question.\n"
            "2. If the input is completely unrecognizable, say: 'Pardon me, I didn't quite catch that. Could you repeat the location or budget?'\n"
            "3. NEVER restart the conversation. If you have the name, always address them by name.\n"
            "4. Track the conversation state strictly: Name -> Area -> Budget -> Unit Type -> Close."

            "If the user input is shorter than 3 characters or nonsensical noise, do not reset. Simply ask 'Pardon me, I didn't quite catch that. Could you repeat that?'"
        )
        
        self.model = genai.GenerativeModel(
            self.model_name,
            system_instruction=self.system_instruction
        )
        self.history = [] 

    async def think(self, text):
        clean_text = text.lower().strip()
        
        # 0.0s Local Greeting
        if any(w in clean_text for w in ["hello", "hi", "hey"]):
            return "Welcome to ATS Global Manhattan. I am your property consultant. May I have your name, please?"

        self.history.append(f"User: {text}")
        prompt = f"User: {text}. Current History: {self.history[-4:]}" 
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.4, 
                    "top_p": 0.8 # Added for better word choice
                }
            )
            
            ai_reply = response.text.strip()
            self.history.append(f"AI: {ai_reply}")

            if "senior partner" in ai_reply.lower() or "goodbye" in ai_reply.lower():
                print("🏁 Closing Deal & Saving Profile...")
                asyncio.create_task(self.generate_mom())

            return ai_reply
            
        except Exception as e:
            print(f"⚠️ Brain Error: {e}")
            return self.smart_fallback()

    def smart_fallback(self):
        hist = " ".join(self.history).lower()
        if "jonathan" not in hist: 
            return "Pardon me, I missed your name. Could you repeat it?"
        if "manhattan" not in hist and "brooklyn" not in hist:
            return "Johnathan, did you say you were interested in Manhattan or Brooklyn?"
        return "I missed that part. Could you please share your budget in millions?"

    async def generate_mom(self):
        if not self.history: return
        print("📝 Exporting Lead Profile to JSON...")
        mom_prompt = (
            f"Transcript: {self.history}. "
            "Create a clean JSON lead profile with these keys: "
            "{'name': '', 'area': '', 'budget_millions': '', 'unit_type': '', 'status': 'VIP Lead'}"
        )
        try:
            summary = await asyncio.to_thread(self.model.generate_content, mom_prompt)
            with open("nyc_lead_profile.json", "w") as f:
                f.write(summary.text)
            # ADD THIS LINE TO SEE IT IN TERMINAL
            print(f"\n✨ NEW LEAD CAPTURED:\n{summary.text}\n")
            print("✅ nyc_lead_profile.json has been updated.")
        except Exception as e:
            print(f"❌ MoM Error: {e}")