import time
import google.generativeai as genai

class CoreLLMClient:
    def __init__(self):
        # 🚨 Ensure your real Gemini API key is here! 🚨
        self.api_key = "AIzaSyBBHMZUWl2XClbtyBIcMUQxjwvZh7IfgW0" 
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def stream_inference(self, system_instruction: str, user_prompt: str):
        """Executes the API call with a strict retry loop and streaming."""
        
        # Combine the system rules and the user data
        full_prompt = f"SYSTEM INSTRUCTION:\n{system_instruction}\n\nUSER PAYLOAD:\n{user_prompt}"
        
        max_retries = 3
        retry_delay = 26 
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                break  
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota" in error_msg:
                    if attempt < max_retries - 1:
                        yield f"\n\n**[⚠️ API RATE LIMIT HIT]** Cooldown required. Retrying in {retry_delay} seconds (Attempt {attempt + 1}/{max_retries})...\n\n"
                        time.sleep(retry_delay)
                    else:
                        yield f"\n\n**[❌ ERROR]** Max retries reached. Rate limit exceeded."
                else:
                    yield f"\n\n**[❌ ERROR]** Connection to Gemini Core failed: {error_msg}"
                    break