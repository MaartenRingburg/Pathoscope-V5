# backend/modules/ai_driver.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# load .env vars
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise RuntimeError('GEMINI_API_KEY not set in .env')

# configure the API
genai.configure(api_key=API_KEY)

# choose model
MODEL_NAME = "gemini-1.5-flash"

def get_gemini_explanation(disease, genes, pathways):
    """
    Call Gemini to explain the disease with gene and pathway context.
    """
    try:
        prompt = (
            f"Explain the disease '{disease}' in simple terms, "
            f"mentioning these genes: {', '.join(genes[:5])}. "
            f"Also mention pathways: {', '.join(pathways[:5])}."
        )
        
        # generate content
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        
        return response.text.strip() if response.text else 'No explanation available.'
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return f"AI explanation unavailable. Error: {str(e)}"