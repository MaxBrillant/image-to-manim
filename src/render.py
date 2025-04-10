"""
Functions for rendering Manim code into videos using Modal
"""
import time
from src.config import supabase
from src.storage import update_code_in_storage

def queue_manim_rendering(session_id, manim_code, narrative, code_path, quality):
    """
    Queue Manim rendering job and handle rendering process with retries.
    
    Args:
        session_id (str): Unique session identifier
        manim_code (str): Generated Manim code to render
        narrative (str): Narrative script for the animation
        code_path (str): Path to the stored Manim code in Supabase
        
    Returns:
        dict: Result containing video_url, error (if any), and current_code
    """
    try:
        from src.modal_renderer import app, ManimRenderer
        
        # Update status
        supabase.table("manim_projects").update({"status": "queued_for_rendering"}).eq("id", session_id).execute()
        
        renderer = ManimRenderer()
        
        # Call the Modal function asynchronously
        with app.run():
            result_future = renderer.render_video.remote(session_id, manim_code, quality)
        
            print(result_future)
            # Check if rendering was successful
            video_url = result_future.get("video_url")
            error_message = result_future.get("error")
            retry_count = 0
            max_retries = 3
            current_code = manim_code
            
            # Handle rendering failures and retries
            while video_url is None and retry_count < max_retries:
                print(f"Rendering failed with error: {error_message}")
                print(f"Regenerating Manim code based on error ({retry_count + 1}/{max_retries})...")
                retry_count += 1
                
                # Import here to avoid circular import
                from src.generation import regenerate_manim_code
                
                # Regenerate the Manim code based on the error
                current_code = regenerate_manim_code(narrative, current_code, error_message, session_id)
                
                # Update code in storage (with error handling)
                update_code_in_storage(code_path, current_code)
                
                # Wait a moment before retrying
                time.sleep(2)
                
                print(f"Retrying rendering job ({retry_count}/{max_retries})...")
                # Make a new render request with the regenerated code
                result_future = renderer.render_video.remote(session_id, current_code, quality)
                print(f"Retry {retry_count} result: {result_future}")
                video_url = result_future.get("video_url")
                error_message = result_future.get("error")
            
            # Return the rendering result
            return {
                "video_url": video_url,
                "error": error_message,
                "current_code": current_code
            }
                
    except Exception as modal_error:
        print(f"Error queuing Modal job: {str(modal_error)}")
        
        # Return error information
        return {
            "video_url": None,
            "error": str(modal_error),
            "current_code": manim_code
        }