"""
Functions for handling storage operations with Supabase
"""
from src.config import supabase

def update_code_in_storage(code_path, code_content):
    """Helper function to update code in Supabase storage with error handling"""
    
    try:
        supabase.storage.from_("manim-generator").upload(
            code_path,
            code_content.encode('utf-8'),
            {    "cacheControl": '3600',    "upsert": "true"  }
        )
        print(f"Uploaded new code to: {code_path}")
    except Exception as upload_error:
        print(f"Error uploading new code file: {str(upload_error)}")
