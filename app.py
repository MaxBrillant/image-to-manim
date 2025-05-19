"""
Main application file for the image-to-manim service
"""
import os
import uuid
import requests
import logging
import time
from io import BytesIO
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

# Import from our modules
from src.config import supabase
from src.generation import generate_problem_analysis, generate_script, generate_manim_code, improve_video_from_feedback
from src.render import queue_manim_rendering
from src.review import review_video
from src.storage import update_code_in_storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger('image-to-manim')

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    logger.info("Health check endpoint accessed")
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/process-image', methods=['POST'])
def process_image():
    """Endpoint to process an image of a math problem and return a detailed description and solution"""
    start_time = time.time()
    logger.info("Starting image processing")
    
    # Check if image is provided
    if 'image' not in request.files:
        logger.error("No image provided in request")
        return jsonify({"error": "No image provided"}), 400
    
    try:
        # Get image from request
        image_file = request.files['image']
        logger.info(f"Image received: {image_file.filename} ({image_file.content_type})")
        img = Image.open(image_file)
        
        # Create a unique session ID for this request
        session_id = str(uuid.uuid4())
        logger.info(f"Generated session ID: {session_id}")
        
        # Upload the original image to Supabase
        logger.info("Uploading image to Supabase storage")
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
        logger.info(f"Storing image at path: {image_path}")
        supabase.storage.from_("manim-generator").upload(
            image_path,
            img_bytes,
            {    "cacheControl": '3600',    "upsert": "true"  }
        )
        
        # Get public URL
        image_url = supabase.storage.from_("manim-generator").get_public_url(image_path)
        logger.info(f"Image accessible at URL: {image_url}")
        
        # Analyze the math problem from the image
        logger.info("Starting math problem analysis")
        problem_analysis = generate_problem_analysis(img)
        logger.info("Math problem analysis completed")
        
        # Store the project metadata in Supabase database
        project_data = {
            "id": session_id,
            "problem_analysis": problem_analysis,
            "status": "image_processed",
            "image_url": image_url,
            "created_at": "now()"
        }
        
        # Insert into database
        logger.info(f"Inserting project data into database with ID: {session_id}")
        supabase.table("manim_projects").insert(project_data).execute()
        
        response = {
            "session_id": session_id,
            "problem_analysis": problem_analysis,
            "image_url": image_url,
            "status": "image_processed",
            "message": "Image processed successfully. Use the session_id to generate a script."
        }
        
        process_time = round(time.time() - start_time, 2)
        logger.info(f"Image processing completed in {process_time}s")
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error in process_image: {str(e)}\n{error_trace}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-script', methods=['POST'])
def generate_script_endpoint():
    """Endpoint to generate a script based on a problem analysis"""
    start_time = time.time()
    logger.info("Starting script generation")
    data = request.json
    
    if not data or 'session_id' not in data:
        logger.error("No session_id provided in request")
        return jsonify({"error": "No session_id provided"}), 400
    
    try:
        session_id = data['session_id']
        logger.info(f"Processing script generation for session: {session_id}")
        
        # Get the project data from Supabase
        logger.info(f"Fetching project data for session: {session_id}")
        response = supabase.table("manim_projects").select("*").eq("id", session_id).execute()
        if not response.data:
            logger.error(f"No project found with session_id: {session_id}")
            return jsonify({"error": f"No project found with session_id: {session_id}"}), 404
        
        project_data = response.data[0]
        
        # Check if the project has been processed
        if not project_data.get('problem_analysis'):
            logger.error(f"Problem analysis not found for session: {session_id}")
            return jsonify({"error": "Problem analysis has not been generated yet"}), 400
        
        # Generate script
        logger.info("Generating script script from problem analysis")
        script = generate_script(project_data['problem_analysis'])
        logger.info("Script generation completed")
        
        # Store script in Supabase
        script_path = f"{session_id}/script.txt"
        logger.info(f"Storing script at path: {script_path}")
        supabase.storage.from_("manim-generator").upload(
            script_path,
            script.encode('utf-8'),
            {    "cacheControl": '3600',    "upsert": "true"  }
        )
        script_url = supabase.storage.from_("manim-generator").get_public_url(script_path)
        logger.info(f"Script accessible at URL: {script_url}")
        
        # Update the project status
        logger.info(f"Updating project status to 'script_generated' for session: {session_id}")
        supabase.table("manim_projects").update({
            "status": "script_generated",
            "script_url": script_url
        }).eq("id", session_id).execute()
        
        response = {
            "session_id": session_id,
            "script_url": script_url,
            "script_text": script,
            "status": "script_generated",
            "message": "Script generated successfully. Use the session_id to generate a video."
        }
        
        process_time = round(time.time() - start_time, 2)
        logger.info(f"Script generation completed in {process_time}s")
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error in generate_script: {str(e)}\n{error_trace}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Endpoint to generate a video from a script"""
    start_time = time.time()
    logger.info("Starting video generation")
    data = request.json
    
    if not data or 'session_id' not in data:
        logger.error("No session_id provided in request")
        return jsonify({"error": "No session_id provided"}), 400
    
    # Optional video quality parameter with default value
    video_quality = data.get('video_quality', 'medium')
    if video_quality not in ['low', 'medium', 'high']:
        logger.warning(f"Invalid video quality '{video_quality}' requested, defaulting to 'medium'")
        video_quality = 'medium'  # Default to medium if invalid quality is provided
    
    try:
        session_id = data['session_id']
        
        # Get the project data from Supabase
        logger.info(f"Fetching project data for session: {session_id}")
        response = supabase.table("manim_projects").select("*").eq("id", session_id).execute()
        if not response.data:
            logger.error(f"No project found with session_id: {session_id}")
            return jsonify({"error": f"No project found with session_id: {session_id}"}), 404
        
        project_data = response.data[0]
        
        # Check if we have a script
        if not project_data.get('script_url'):
            logger.error(f"Script URL not found for session: {session_id}")
            return jsonify({"error": "Script has not been generated yet"}), 400
        
        # Get the script from the stored URL
        script_url = project_data.get('script_url')
        logger.info(f"Retrieving script from URL: {script_url}")
        
        try:
            # Download the script content from the URL
            response = requests.get(script_url)
            if response.status_code == 200:
                script = response.text
                logger.info("Successfully retrieved script content")
            else:
                logger.error(f"Failed to retrieve script. Status code: {response.status_code}")
                return jsonify({"error": f"Failed to retrieve script. Status code: {response.status_code}"}), 500
        except Exception as e:
            logger.error(f"Exception while retrieving script: {str(e)}")
            return jsonify({"error": f"Failed to retrieve script: {str(e)}"}), 500
        
        # Generate Manim code
        logger.info("Generating Manim code from script")
        manim_code = generate_manim_code(script, session_id)
        logger.info("Manim code generation completed")
        
        # Store Manim code in Supabase
        code_path = f"{session_id}/scene.py"
        logger.info(f"Storing Manim code at path: {code_path}")
        update_code_in_storage(code_path, manim_code)
        code_url = supabase.storage.from_("manim-generator").get_public_url(code_path)
        logger.info(f"Manim code accessible at URL: {code_url}")
        
        # Update the project data
        logger.info(f"Updating project with code URL for session: {session_id}")
        supabase.table("manim_projects").update({
            "code_url": code_url
        }).eq("id", session_id).execute()
        
        # Queue the Manim rendering job on Modal
        logger.info(f"Queuing Manim rendering job with quality: {video_quality}")
        
        # Add video quality to the rendering parameters
        render_result = queue_manim_rendering(
            session_id=session_id,
            manim_code=manim_code,
            script=script,
            code_path=f"{session_id}/scene.py",
            quality=video_quality
        )
        
        video_url = render_result.get("video_url")
        error_message = render_result.get("error")
        
        if video_url:
            logger.info(f"Rendering completed successfully, video URL: {video_url}")
            # Update the project status
            logger.info(f"Updating project status to 'video_generated' for session: {session_id}")
            supabase.table("manim_projects").update({
                "status": "video_generated",
                "video_url": video_url
            }).eq("id", session_id).execute()
            
            response = {
                "session_id": session_id,
                "script_url": script_url,
                "code_url": code_url,
                "video_url": video_url,
                "status": "video_generated",
                "message": "Video generated successfully."
            }
        else:
            # Rendering failed
            logger.error(f"Video rendering failed: {error_message}")
            response = {
                "session_id": session_id,
                "script_url": script_url,
                "code_url": code_url,
                "status": "code_generated",
                "message": "Code generation complete, but video rendering failed.",
                "error": error_message
            }
        
        process_time = round(time.time() - start_time, 2)
        logger.info(f"Video generation process completed in {process_time}s")
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error in generate_video: {str(e)}\n{error_trace}")
        return jsonify({"error": str(e)}), 500

@app.route('/improve-video', methods=['POST'])
def improve_video():
    """Endpoint to review and improve a generated video"""
    start_time = time.time()
    logger.info("Starting video improvement process")
    data = request.json
    
    if not data or 'session_id' not in data:
        logger.error("No session_id provided in request")
        return jsonify({"error": "No session_id provided"}), 400
    
    # Optional video quality parameter with default value
    video_quality = data.get('video_quality', 'medium')
    if video_quality not in ['low', 'medium', 'high']:
        logger.warning(f"Invalid video quality '{video_quality}' requested, defaulting to 'medium'")
        video_quality = 'medium'  # Default to medium if invalid quality is provided
    
    try:
        session_id = data['session_id']
        
        # Get the project data from Supabase
        logger.info(f"Fetching project data for session: {session_id}")
        response = supabase.table("manim_projects").select("*").eq("id", session_id).execute()
        if not response.data:
            logger.error(f"No project found with session_id: {session_id}")
            return jsonify({"error": f"No project found with session_id: {session_id}"}), 404
        
        project_data = response.data[0]
        
        # Check if we have a video to improve
        if not project_data.get('video_url'):
            logger.error(f"Video URL not found for session: {session_id}")
            return jsonify({"error": "Video has not been generated yet"}), 400
        
        video_url = project_data.get('video_url')
        code_url = project_data.get('code_url')
        script_url = project_data.get('script_url')
        
        # Review the video
        logger.info(f"Reviewing video quality at URL: {video_url}")
        review_result = review_video(video_url)
        
        score = review_result["score"]
        review_text = review_result["review"]
        needs_improvement = review_result["needs_improvement"]
        logger.info(f"Video review completed. Score: {score}/100. Needs improvement: {needs_improvement}")
        
        # Update the database with review results
        logger.info(f"Updating project status to 'review_complete' for session: {session_id}")
        supabase.table("manim_projects").update({
            "status": "review_complete",
        }).eq("id", session_id).execute()
        
        # If the video needs improvement
        if needs_improvement:
            logger.info(f"Video quality score is low ({score}/100). Regenerating based on feedback")
            
            # Get the script from the stored URL
            logger.info(f"Retrieving script from URL: {script_url}")
            
            try:
                # Download the script content from the URL
                response = requests.get(script_url)
                if response.status_code == 200:
                    script = response.text
                    logger.info("Successfully retrieved script content")
                else:
                    logger.error(f"Failed to retrieve script. Status code: {response.status_code}")
                    return jsonify({"error": f"Failed to retrieve script. Status code: {response.status_code}"}), 500
            except Exception as e:
                logger.error(f"Exception while retrieving script: {str(e)}")
                return jsonify({"error": f"Failed to retrieve script: {str(e)}"}), 500
            
            # Get the manim code from the stored URL
            logger.info(f"Retrieving manim code from URL: {code_url}")
            
            try:
                # Download the manim code content from the URL
                response = requests.get(code_url)
                if response.status_code == 200:
                    manim_code = response.text
                    logger.info("Successfully retrieved manim code content")
                else:
                    logger.error(f"Failed to retrieve manim code. Status code: {response.status_code}")
                    return jsonify({"error": f"Failed to retrieve manim code. Status code: {response.status_code}"}), 500
            except Exception as e:
                logger.error(f"Exception while retrieving manim code: {str(e)}")
                return jsonify({"error": f"Failed to retrieve manim code: {str(e)}"}), 500
            
            # Attempt to improve the video based on feedback
            logger.info("Attempting to improve video based on feedback")
            improved_result = improve_video_from_feedback(
                session_id,
                manim_code,
                review_text,
                script,
                score,
                f"{session_id}/scene.py"  # code path
            )
            
            if improved_result.get("success", False):
                # Video was successfully improved
                logger.info("Successfully generated improved manim code")
                improved_code = improved_result.get("improved_code")
                
                # Store the improved code
                logger.info(f"Storing improved manim code")
                update_code_in_storage(f"{session_id}/scene.py", improved_code)
                
                logger.info(f"Queuing improved Manim rendering job with quality: {video_quality}")
                # Call the function to queue the rendering job with quality parameter
                render_result = queue_manim_rendering(
                    session_id=session_id,
                    manim_code=improved_code,
                    script=script,
                    code_path=f"{session_id}/scene.py",
                    quality=video_quality
                )
                
                improved_video_url = render_result.get("video_url")
                
                if improved_video_url:
                    # Update the database with the improved video
                    logger.info(f"Rendering of improved video completed successfully, URL: {improved_video_url}")
                    logger.info(f"Updating project status to 'improved_render_complete' for session: {session_id}")
                    supabase.table("manim_projects").update({
                        "status": "improved_render_complete",
                        "video_url": improved_video_url,
                    }).eq("id", session_id).execute()
                    
                    response = {
                        "session_id": session_id,
                        "improved_video_url": improved_video_url,
                        "code_url": code_url,
                        "script_url": script_url,
                        "status": "improved_render_complete",
                        "review_score": score,
                        "review_text": review_text,
                        "message": f"Video has been improved based on feedback. Original score: {score}/100."
                    }
                else:
                    # Improvement rendering failed
                    error = render_result.get("error", "Unknown error during rendering")
                    logger.error(f"Improved video rendering failed: {error}")
                    response = {
                        "session_id": session_id,
                        "code_url": code_url,
                        "script_url": script_url,
                        "status": "review_complete",
                        "review_score": score,
                        "review_text": review_text,
                        "message": f"Video was reviewed (score: {score}/100), but improvement rendering failed: {error}"
                    }
            else:
                # Improvement attempt failed
                error = improved_result.get("error", "Unknown error during improvement")
                logger.error(f"Failed to improve video: {error}")
                response = {
                    "session_id": session_id,
                    "code_url": code_url,
                    "script_url": script_url,
                    "status": "review_complete",
                    "review_score": score,
                    "review_text": review_text,
                    "message": f"Video was reviewed (score: {score}/100), but improvement failed: {error}"
                }
        else:
            # No improvement needed
            logger.info(f"Video doesn't need improvement (score: {score}/100)")
            response = {
                "session_id": session_id,
                "improved_video_url": video_url,
                "code_url": code_url,
                "script_url": script_url,
                "status": "review_complete",
                "review_score": score,
                "review_text": review_text,
                "message": f"Video was reviewed. Score: {score}/100. No improvement needed."
            }
        
        process_time = round(time.time() - start_time, 2)
        logger.info(f"Video improvement process completed in {process_time}s")
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error in improve_video: {str(e)}\n{error_trace}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=True)
