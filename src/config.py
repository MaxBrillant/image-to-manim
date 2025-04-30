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
    with open("resources/script-prompt.txt", "r") as f:
        script_prompt_template = f.read()
    with open("resources/manim_code_guide.txt", "r") as f:
        manim_code_guide = f.read()
    with open("resources/manim_guidelines.txt", "r") as f:
        manim_guidelines = f.read()
    with open("resources/3blue1brown_philosophy.md", "r") as f:
        philosophy = f.read()
    with open("resources/video-quality-standards.md", "r") as f:
        video_quality_standards = f.read()
    
    return script_prompt_template, manim_code_guide, manim_guidelines, philosophy, video_quality_standards

# Initialize on import
SCRIPT_PROMPT_TEMPLATE, MANIM_CODE_GUIDE, MANIM_GUIDELINES, PHILOSOPHY, VIDEO_QUALITY_STANDARDS = load_prompt_templates()
