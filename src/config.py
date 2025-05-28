"""
Configuration and initialization for the application
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load prompt templates
def load_prompt_templates():
    """Load prompt templates from resources directory"""
    with open("resources/manim_code_guide.txt", "r") as f:
        manim_code_guide = f.read()
    with open("resources/video-quality-standards.md", "r") as f:
        video_quality_standards = f.read()
    
    return manim_code_guide, video_quality_standards

# Initialize on import
MANIM_CODE_GUIDE, VIDEO_QUALITY_STANDARDS = load_prompt_templates()
