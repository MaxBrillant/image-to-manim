import os
import base64
from io import BytesIO
import json
import requests
from flask import Flask, request, jsonify
from litellm import completion
from flask_cors import CORS
from PIL import Image
from dotenv import load_dotenv
import tempfile
import subprocess
import uuid
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check if Manim is installed
try:
    subprocess.run(["manim", "--version"], capture_output=True, text=True)
    print("Manim installation found.")
except:
    print("WARNING: Manim might not be installed or not in PATH")

# Load narrative prompt template
with open("resources/narrative-prompt.txt", "r") as f:
    NARRATIVE_PROMPT_TEMPLATE = f.read()

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
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        
        # Upload to Supabase storage
        image_path = f"{session_id}/original.jpg"
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
        try:
            from modal_renderer import app, ManimRenderer
            
            # Update status
            supabase.table("manim_projects").update({"status": "queued_for_rendering"}).eq("id", session_id).execute()
            
            renderer = ManimRenderer()
            # Call the Modal function asynchronously
            with app.run():
                result_future = renderer.render_video.remote(session_id, manim_code)
            
                print(result_future)
                # Check if video_url is null and retry up to 3 times
                video_url = result_future.get("video_url")
                retry_count = 0
                max_retries = 3
                
                while video_url is None and retry_count < max_retries:
                    print(f"Video URL is None, retrying render request ({retry_count + 1}/{max_retries})...")
                    retry_count += 1
                    # Wait a moment before retrying
                    import time
                    time.sleep(2)
                    # Make a new render request
                    result_future = renderer.render_video.remote(session_id, manim_code)
                    print(f"Retry {retry_count} result: {result_future}")
                    video_url = result_future.get("video_url")
                
                # Update project with video URL
                supabase.table("manim_projects").update({
                    "status": "render_complete",
                    "video_url": video_url,
                }).eq("id", session_id).execute()
            
                # Return response with details
                response = {
                    "session_id": session_id,
                    "narrative": narrative,
                    "narrative_url": narrative_url,
                    "video_url": video_url,
                    "code_url": code_url,
                    "image_url": image_url,
                    "status": "render_complete",
                    "message": "Processing complete - video has been rendered and is available."
                }
                    
                return jsonify(response)
            
        except Exception as modal_error:
            print(f"Error queuing Modal job: {str(modal_error)}")
            
            # Return response with details but note rendering wasn't started
            response = {
                "session_id": session_id,
                "narrative": narrative,
                "narrative_url": narrative_url,
                "code_url": code_url,
                "image_url": image_url,
                "status": "code_generated",
                "message": "Code generation complete, but video rendering could not be queued.",
                "error": str(modal_error)
            }
                
            return jsonify(response)
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def generate_narrative(image, session_id):
    """Generate narrative script from image using liteLLM with AWS Bedrock"""
    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Set up environment for liteLLM with AWS Bedrock
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
    os.environ["AWS_REGION_NAME"] = "us-west-2"  # Set your AWS region

    
    try:
        # Use liteLLM's completion method with AWS Bedrock
        response = completion(
            model = "bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": NARRATIVE_PROMPT_TEMPLATE
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64," + img_str,
                    },
                }
                ]
            }],
            temperature=0.4,
            max_tokens=8192
        )
        
        # Extract the content from the response
        narrative = response.choices[0].message.content
        return narrative
        
    except Exception as e:
        print(f"Error generating narrative: {str(e)}")
        raise Exception(f"Failed to generate narrative: {str(e)}")

def generate_manim_code(narrative, session_id):
    """Generate Manim code from narrative using liteLLM with AWS Bedrock"""
    # Set up environment for liteLLM with AWS Bedrock
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
    os.environ["AWS_REGION_NAME"] = "us-west-2"  # Set your AWS region
    
    # Prompt for generating Manim code with precise timing
    prompt = f"""
Generate complete, executable Manim Python code that precisely visualizes this educational narrative:

{narrative}

Your code must:
1. Create a single Scene class implementing all [VISUAL: description] elements
2. Time animations exactly according to [t=X:XX] markers (minutes:seconds)
3. Calculate precise wait() durations between timing points
4. Create smooth transitions with proper spacing between elements
5. Follow 3Blue1Brown-style best practices for educational animations

Below is an example of correctly formatted code based on a sample narrative:

EXAMPLE NARRATIVE:
[t=0:00] Let's explore the concept of derivatives.
[VISUAL: Show the equation f(x) = x²]
[t=0:10] The derivative measures the rate of change of a function.
[VISUAL: Draw a tangent line to the parabola]
[t=0:25] As we move along the curve, the slope of this tangent line changes.
[VISUAL: Animate the tangent line moving along the curve]
[t=0:40] This changing slope is precisely what the derivative function f'(x) = 2x represents.
[VISUAL: Show the equation f'(x) = 2x alongside the original function]

EXAMPLE CODE:
```python
from manim import *

class DerivativeExample(Scene):
    def construct(self):
        # [t=0:00] Start of animation
        
        # [VISUAL: Show the equation f(x) = x²]
        function_eq = MathTex(r"f(x) = x^2").scale(1.5)
        self.play(Write(function_eq), run_time=3)
        self.wait(7)  # Wait until t=0:10
        
        # [t=0:10] The derivative measures the rate of change
        function_eq.generate_target()
        function_eq.target.move_to(UP*2)
        self.play(MoveToTarget(function_eq), run_time=2)
        
        # Create axes and parabola
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
        ).add_coordinates()
        
        graph = axes.plot(lambda x: x**2, color=YELLOW)
        graph_label = axes.get_graph_label(graph, "f(x)=x^2", x_val=2, direction=UP)
        
        graph_group = VGroup(axes, graph, graph_label)
        graph_group.scale(0.7).shift(DOWN*0.5)
        
        self.play(Create(axes), run_time=2)
        self.play(Create(graph), run_time=2)
        self.play(Write(graph_label), run_time=1)
        self.wait(8)  # Continue waiting until t=0:25
        
        # [t=0:25] Draw a tangent line
        x_tracker = ValueTracker(1)
        
        def get_tangent_line():
            x = x_tracker.get_value()
            slope = 2*x
            point = axes.coords_to_point(x, x**2)
            line = Line(
                point + LEFT * 3,
                point + RIGHT * 3,
                color=RED
            ).set_slope(slope)
            return line
        
        tangent = always_redraw(get_tangent_line)
        self.play(Create(tangent), run_time=2)
        
        # [t=0:40] Animate the tangent moving along the curve
        self.play(x_tracker.animate.set_value(-2), run_time=7)
        self.play(x_tracker.animate.set_value(2), run_time=6)
        
        # [VISUAL: Show the derivative equation]
        derivative_eq = MathTex(r"f'(x) = 2x").scale(1.5).next_to(function_eq, DOWN*2)
        self.play(Write(derivative_eq), run_time=3)
        self.wait(2)
"""

    try:
        # Use liteLLM's completion method with AWS Bedrock
        response = completion(
            model="bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.4,
            top_p=0.9,
            max_tokens=8192
        )
        
        # Extract the content from the response
        manim_code = response.choices[0].message.content
        
        # Extract code if it's wrapped in markdown code blocks
        if "```python" in manim_code and "```" in manim_code:
            import re
            code_blocks = re.findall(r'```python\n(.*?)```', manim_code, re.DOTALL)
            if code_blocks:
                manim_code = code_blocks[0]
        
        # Add comment with session id
        manim_code = f"# Generated Manim code for session: {session_id}\n\n{manim_code}"
        
        return manim_code
        
    except Exception as e:
        print(f"Error generating Manim code: {str(e)}")
        raise Exception(f"Failed to generate Manim code: {str(e)}")

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
