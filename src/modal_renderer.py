import os
import random
import tempfile
import re
import subprocess
from io import BytesIO
from pathlib import Path
from modal import Image, App, method, fastapi_endpoint, Mount, Secret

# Define the Modal image with Manim dependencies
manim_image = (
    Image.debian_slim(python_version="3.11")  # Using latest stable Python version
    .apt_install(
        "build-essential",
        "python3-dev",
        "python3-pip",
        "ffmpeg",
        "libcairo2-dev",
        "libpango1.0-dev",
        "texlive-full",
        "tipa",
        "libcairo2",
        "libpango-1.0-0",
        "libpangocairo-1.0-0",
        "sox",
    )
    .pip_install(
        "manim==0.17.0",
        "supabase",
        "python-dotenv",
        "fastapi[standard]",  # Required for fastapi_endpoint
    )
)

# Create an App with the image and secrets
app = App("manim-renderer", image=manim_image, secrets=[Secret.from_name("supabase-secrets")])

# Modal class for rendering
@app.cls(gpu="A10G", timeout=300)
class ManimRenderer:
    def __enter__(self):
        # Get environment variables from secrets
        supabase_url = os.environ["SUPABASE_URL"]
        supabase_key = os.environ["SUPABASE_KEY"]
        
        from supabase import create_client, Client
        self.supabase = create_client(supabase_url, supabase_key)
        
        
    @method()
    def render_video(self, session_id, manim_code, quality):
        """Render a Manim video based on provided code"""
        try:
            # Ensure supabase is initialized
            self.__enter__()
            
            # Mark project as rendering in Supabase
            self.supabase.table("manim_projects").update(
                {"status": "rendering"}
            ).eq("id", session_id).execute()
            
            # Create a temporary directory for rendering
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write the code to a temporary file
                local_code_path = os.path.join(temp_dir, "scene.py")
                with open(local_code_path, "w", encoding="utf-8") as f:
                    f.write(manim_code)
                
                # Detect the scene class
                scene_class = "EducationalScene"  # Default
                class_matches = re.findall(r'class\s+(\w+)\s*\(\s*Scene\s*\)', manim_code)
                if class_matches:
                    scene_class = class_matches[0]
                
                # Run Manim command
                cmd = [
                    "python3", "-m", "manim",
                    "-qm" if quality == "medium" else "-ql" if quality == "low" else "-qh",
                    "--media_dir", temp_dir,
                    local_code_path,
                    scene_class
                ]
                
                # Execute the command
                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode != 0:
                    # Update project status to failed
                    self.supabase.table("manim_projects").update({
                        "status": "render_failed",
                    }).eq("id", session_id).execute()
                    
                    return {
                        "status": "error",
                        "message": "Manim rendering failed",
                        "error": process.stderr
                    }
                
                # Find the rendered video
                videos_dir = os.path.join(temp_dir, "videos")
                if not os.path.exists(videos_dir):
                    self.supabase.table("manim_projects").update({
                        "status": "render_failed",
                    }).eq("id", session_id).execute()
                    
                    return {
                        "status": "error",
                        "message": "No video directory created"
                    }
                
                # Find the most recently created MP4 file
                mp4_files = []
                for root, dirs, files in os.walk(videos_dir):
                    for file in files:
                        if file.endswith(".mp4"):
                            mp4_files.append(os.path.join(root, file))
                
                if not mp4_files:
                    self.supabase.table("manim_projects").update({
                        "status": "render_failed",
                    }).eq("id", session_id).execute()
                    
                    return {
                        "status": "error",
                        "message": "No video file was generated"
                    }
                
                video_path = max(mp4_files, key=os.path.getsize)
                
                # Upload video to Supabase
                with open(video_path, "rb") as video_file:
                    video_bytes = video_file.read()
                    
                    # Define path in Supabase storage
                    storage_video_path = f"{session_id}/{random.randint(100000, 999999)}.mp4"
                    
                    # Upload
                    self.supabase.storage.from_("manim-generator").upload(
                        storage_video_path,
                        video_bytes,
                        {
                            "content-type": "video/mp4",
                            "upsert": "true"
                        }
                    )
                    
                    # Get public URL
                    video_url = self.supabase.storage.from_("manim-generator").get_public_url(storage_video_path)
                    
                    # Update project status
                    self.supabase.table("manim_projects").update({
                        "status": "render_complete",
                        "video_url": video_url
                    }).eq("id", session_id).execute()
                    
                    return {
                        "session_id": session_id,
                        "status": "render_complete",
                        "video_url": video_url,
                        "message": "Video rendering complete."
                    }
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(error_details)
            
            # Update project status to failed
            try:
                self.supabase.table("manim_projects").update({
                    "status": "render_failed",
                }).eq("id", session_id).execute()
            except:
                pass
            
            return {
                "status": "error", 
                "error": str(e), 
                "details": error_details
            }
    
    @fastapi_endpoint(method="POST")
    async def render_api(self, session_id: str, manim_code: str):
        """Web endpoint for rendering videos"""
        result = self.render_video(session_id, manim_code)
        return result
