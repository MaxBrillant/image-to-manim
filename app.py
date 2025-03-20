"""
Main application file for the image-to-manim service
"""
import os
import uuid
from io import BytesIO
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

# Import from our modules
from src.config import supabase
from src.generation import generate_narrative, generate_manim_code, improve_video_from_feedback
from src.render import queue_manim_rendering
from src.review import review_video

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/process-image', methods=['POST'])
def process_image():
    """Main endpoint to process an image through the entire pipeline"""
    print("Processing image...")
    # Check if image is provided
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        # Get image from request
        image_file = request.files['image']
        img = Image.open(image_file)
        
        # Create a unique session ID for this request
        session_id = str(uuid.uuid4())
        
        # Step 1: Upload the original image to Supabase
        print("Uploading image to Supabase...")
        # Detect original format or use JPEG as fallback
        img_format = image_file.content_type.split('/')[-1] if image_file.content_type else 'jpeg'
        if img_format.lower() not in ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff', 'webp']:
            img_format = 'jpeg'  # Default to JPEG for unsupported formats
        
        # Use original extension for the file path
        file_ext = img_format.lower()
        if file_ext == 'jpeg':
            file_ext = 'jpg'
        
        buffered = BytesIO()
        img.save(buffered, format=img_format.upper())
        img_bytes = buffered.getvalue()
        
        # Upload to Supabase storage with correct extension
        image_path = f"{session_id}/original.{file_ext}"
        supabase.storage.from_("manim-generator").upload(
            image_path,
            img_bytes
        )
        
        # Get public URL
        image_url = supabase.storage.from_("manim-generator").get_public_url(image_path)
        
        # Step 2: Generate narrative script
        print("Generating narrative script...")
        narrative = generate_narrative(img, session_id)
        
        # Store narrative in Supabase
        narrative_path = f"{session_id}/narrative.txt"
        supabase.storage.from_("manim-generator").upload(
            narrative_path,
            narrative.encode('utf-8')
        )
        narrative_url = supabase.storage.from_("manim-generator").get_public_url(narrative_path)
        
        # Step 3: Generate Manim code
        print("Generating Manim code...")
        manim_code = generate_manim_code(narrative, session_id)
        
        # Store Manim code in Supabase
        code_path = f"{session_id}/scene.py"
        supabase.storage.from_("manim-generator").upload(
            code_path,
            manim_code.encode('utf-8')
        )
        code_url = supabase.storage.from_("manim-generator").get_public_url(code_path)
        
        # Step 4: Store the project metadata in Supabase database
        project_data = {
            "id": session_id,
            "status": "code_generated",
            "narrative": narrative,
            "narrative_url": narrative_url,
            "code_url": code_url,
            "image_url": image_url,
            "created_at": "now()"
        }
        
        # Insert into database
        supabase.table("manim_projects").insert(project_data).execute()
        
        # Step 5: Queue the Manim rendering job on Modal
        print("Queuing Manim rendering job...")
        
        # Call the function to queue the rendering job
        render_result = queue_manim_rendering(
            session_id=session_id,
            manim_code=manim_code,
            narrative=narrative,
            code_path=code_path
        )
        
        video_url = render_result.get("video_url")
        error_message = render_result.get("error")
        current_code = render_result.get("current_code", manim_code)
        
        if video_url:
            # Review the video quality and gather feedback
            print("Reviewing video quality...")
            review_result = review_video(video_url, narrative)
            
            score = review_result["score"]
            review_text = review_result["review"]
            needs_improvement = review_result["needs_improvement"]
            
            # If score is low, regenerate the Manim code and re-render
            feedback_retry_count = 0
            max_feedback_retries = 1  # Limit to one feedback-based retry
            
            if needs_improvement and feedback_retry_count < max_feedback_retries:
                print(f"Video quality score is low ({score}/100). Regenerating based on feedback...")
                feedback_retry_count += 1
                
                # Attempt to improve the video based on feedback
                improved_result = improve_video_from_feedback(
                    session_id, 
                    current_code, 
                    narrative, 
                    review_text, 
                    score, 
                    code_path
                )
                
                if improved_result.get("success", False):
                    # Video was successfully improved
                    improved_code = improved_result.get("improved_code")
                    
                    print("Queuing improved Manim rendering job...")
                    # Call the function to queue the rendering job
                    render_result = queue_manim_rendering(
                        session_id=session_id,
                        manim_code=improved_code,
                        narrative=narrative,
                        code_path=code_path
                    )
                    video_url = render_result.get("video_url")

                    if video_url:
                        # Use the improved video URL for the response
                        response = {
                            "session_id": session_id,
                            "narrative": narrative,
                            "narrative_url": narrative_url,
                            "video_url": video_url,  # This is the improved video URL
                            "code_url": code_url,
                            "image_url": image_url,
                            "status": "improved_render_complete",
                            "original_review": {
                                "score": score,
                                "review": review_text
                            },
                            "improved_review": {
                                "score": score,
                                "review": review_text
                            },
                            "message": f"Processing complete - video has been improved based on feedback. Original score: {score}/100."
                        }
                else:
                    # Improvement attempt failed, use the original video
                    error = improved_result.get("error", "Unknown error")
                    response = {
                        "session_id": session_id,
                        "narrative": narrative,
                        "narrative_url": narrative_url,
                        "video_url": video_url,
                        "code_url": code_url,
                        "image_url": image_url,
                        "status": "review_complete",
                        "review": {
                            "score": score,
                            "review": review_text
                        },
                        "message": f"Processing complete - video has been reviewed (score: {score}/100). Improvement attempt failed: {error}"
                    }
            else:
                # No improvement needed or already at max retries, return with review information
                response = {
                    "session_id": session_id,
                    "narrative": narrative,
                    "narrative_url": narrative_url,
                    "video_url": video_url,
                    "code_url": code_url,
                    "image_url": image_url,
                    "status": "review_complete",
                    "review": {
                        "score": score,
                        "review": review_text
                    },
                    "message": f"Processing complete - video has been rendered and reviewed. Score: {score}/100."
                }
        else:
            # Rendering failed
            response = {
                "session_id": session_id,
                "narrative": narrative,
                "narrative_url": narrative_url,
                "code_url": code_url,
                "image_url": image_url,
                "status": "code_generated",
                "message": "Code generation complete, but video rendering failed.",
                "error": error_message
            }
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
