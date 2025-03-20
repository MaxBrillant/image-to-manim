"""
Configuration and initialization for the application
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load prompt templates
def load_prompt_templates():
    """Load prompt templates from resources directory"""
    with open("resources/narrative-prompt.txt", "r") as f:
        narrative_prompt_template = f.read()
    
    with open("resources/manim-prompt.txt", "r") as f:
        manim_prompt_template = f.read()
    
    return narrative_prompt_template, manim_prompt_template

# Initialize on import
NARRATIVE_PROMPT_TEMPLATE, MANIM_PROMPT_TEMPLATE = load_prompt_templates()
