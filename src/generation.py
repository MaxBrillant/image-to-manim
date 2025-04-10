"""
Functions for generating narrative and Manim code from images
"""
import os
import re
import base64
from io import BytesIO
from PIL import Image
from litellm import completion
import litellm

from src.config import (
    AWS_ACCESS_KEY_ID, 
    AWS_SECRET_ACCESS_KEY, 
    NARRATIVE_PROMPT_TEMPLATE,
    MANIM_PROMPT_TEMPLATE
)
from src.storage import update_code_in_storage

# litellm._turn_on_debug()

def generate_problem_analysis(image):
    """Generate narrative script from image using liteLLM with AWS Bedrock"""
    # Convert image to base64 preserving its format
    buffered = BytesIO()
    img_format = image.format if image.format else "JPEG"
    image.save(buffered, format=img_format)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Determine the MIME type for the base64 string
    mime_type = f"image/{img_format.lower()}"
    if mime_type == "image/jpg":
        mime_type = "image/jpeg"
    
    # Set up environment for liteLLM with AWS Bedrock
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
    os.environ["AWS_REGION_NAME"] = "us-west-2"  # Set your AWS region
    
    try:
        
        # Use liteLLM's completion method with AWS Bedrock
        response = litellm.completion(
            model = "bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            messages=[{
                "role": "system",
                "content": f"""
                    You are a world-class mathematical educator with expertise in analysing math problems and providing well described solutions. 
                    Your task is to analyze the provided image and generate a detailed analysis that describes the problem depicted in the image.
                    Understand every detail of the image and provide a comprehensive analysis of the problem, including:
                    1. A clear and detailed description of the problem
                    2. The mathematical concepts involved
                    3. The steps needed to solve the problem
                    4. Any potential pitfalls or common mistakes
                    5. The overall educational value of the problem
                    6. The target audience for the problem
                    7. The level of difficulty of the problem
                    8. Any additional insights or comments
                    9. Provide the analysis in a clear and structured format.

                    ## CRITICAL PRIORITY: MATHEMATICAL CORRECTNESS

                    MATHEMATICAL ACCURACY IS THE ABSOLUTE HIGHEST PRIORITY. Never sacrifice correctness for any reason.

                    1. **Verify every mathematical statement** before including it in your narrative
                    2. **Double-check all solutions** using first principles and standard mathematical techniques
                    3. **Do not hallucinate solutions** - if you're uncertain about any step, omit it entirely
                    4. **Only include mathematically proven facts** - no approximations or simplifications that compromise accuracy
                    5. **When analyzing the problem image**, ensure your solution matches exactly what's shown, without adding assumptions
                    """
                    ,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "role": "user",
                "content": [
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64," + img_str,
                    },
                }
                ],
                "cache_control": {"type": "ephemeral"},
            }],
            max_tokens=8192,
            thinking={"type": "enabled", "budget_tokens": 1024},
        )
        
        # Extract the content from the response
        narrative = response.choices[0].message.content
        return narrative
        
    except Exception as e:
        print(f"Error generating problem analysis: {str(e)}")
        raise Exception(f"Failed to generate problem analysis: {str(e)}")
    

def generate_narrative(problem_analysis):
    """Generate narrative script from problem analysis using liteLLM with AWS Bedrock"""
    
    # Set up environment for liteLLM with AWS Bedrock
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
    os.environ["AWS_REGION_NAME"] = "us-east-1"  # Set your AWS region
    
    try:
        
        # Use liteLLM's completion method with AWS Bedrock
        response = litellm.completion(
            model = "bedrock/converse/us.deepseek.r1-v1:0",
            messages=[{
                "role": "system",
                "content": NARRATIVE_PROMPT_TEMPLATE,
            },
            {
                "role": "user",
                "content": f"PROBLEM ANALYSIS: \n{problem_analysis}"
            }],
            temperature=0.4,
            max_tokens=8192,
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
    os.environ["AWS_REGION_NAME"] = "us-east-1"  # Set your AWS region
    
    try:
        # Load the manim code guide
        manim_guide_path = os.path.join("resources", "manim_code_guide.txt")
        with open(manim_guide_path, "r") as guide_file:
            manim_code_guide = guide_file.read()
        
        # Create an enhanced prompt with the code guide
        enhanced_prompt = MANIM_PROMPT_TEMPLATE + "\n\n# MANIM CODE GUIDE REFERENCE\n" + manim_code_guide
        
        # Use liteLLM's completion method with AWS Bedrock
        response = litellm.completion(
            model="bedrock/converse/us.deepseek.r1-v1:0",
            messages=[{
                "role": "system",
                "content": f"""
                    You are an expert Manim developer. You need to create a Manim animation that visualizes the provided narrative.

                    Ensure the Manim code generated ONLY refers to the MANIM CODE GUIDE REFERENCE

                    MANIM CODE GUIDE REFERENCE:
                    {manim_code_guide}
                    """
            },
            {
                "role": "user",
                "content": "NARRATIVE: \n" + narrative
            }],
            temperature=0.4,
            max_tokens=8192,
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


def regenerate_manim_code(narrative, previous_code, error_message, session_id):
    """Regenerate Manim code based on previous code and error message"""
    # Set up environment for liteLLM with AWS Bedrock
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
    os.environ["AWS_REGION_NAME"] = "us-east-1"  # Set your AWS region
    
    try:
        # Load the manim code guide
        manim_guide_path = os.path.join("resources", "manim_code_guide.txt")
        with open(manim_guide_path, "r") as guide_file:
            manim_code_guide = guide_file.read()

        # Use liteLLM's completion method with AWS Bedrock
        response = litellm.completion(
            model="bedrock/converse/us.deepseek.r1-v1:0",
            messages=[{
                "role": "system",
                "content": f"""You are an expert Manim developer. You need to fix the following Manim code that failed to render.

                    Please analyze the error message carefully and fix the Manim code to create a working animation that visualizes the narrative. 
                    Make sure to:
                    1. Fix any syntax errors or bugs in the code
                    2. Simplify complex animations that might be causing rendering issues
                    3. Ensure the Manim code generated ONLY refers to the MANIM CODE GUIDE REFERENCE

                    NARRATIVE TO VISUALIZE:
                    {narrative}

                    # MANIM CODE GUIDE REFERENCE:
                    {manim_code_guide}
                    """
            },
                      {
                "role": "user",
                "content": f"""
                    ERROR MESSAGE:
                    {error_message[-5000:]}

                    PREVIOUS CODE:
                    ```python
                    {previous_code}
                    ```
                    """
            }],
            temperature=0.2,
            max_tokens=8192,
        )
        
        # Extract the content from the response
        fixed_code = response.choices[0].message.content
        
        # Extract code if it's wrapped in markdown code blocks
        if "```python" in fixed_code and "```" in fixed_code:
            import re
            code_blocks = re.findall(r'```python\n(.*?)```', fixed_code, re.DOTALL)
            if code_blocks:
                fixed_code = code_blocks[0]
        
        # Add comment with session id and retry information
        fixed_code = f"# Regenerated Manim code for session: {session_id}\n# Fixed version after rendering error\n\n{fixed_code}"
        
        print(f"Successfully regenerated Manim code based on error")
        return fixed_code
        
    except Exception as e:
        print(f"Error regenerating Manim code: {str(e)}")
        # If regeneration fails, return the original code
        print("Returning original code due to regeneration failure")
        return previous_code


def improve_video_from_feedback(session_id, current_code, review_text, narrative, score, code_path):
    """Function to improve video based on feedback reviews"""
    
    # Set up environment for liteLLM with AWS Bedrock
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
    os.environ["AWS_REGION_NAME"] = "us-east-1"
    
    try:
        # Load the manim code guide
        manim_guide_path = os.path.join("resources", "manim_code_guide.txt")
        with open(manim_guide_path, "r") as guide_file:
            manim_code_guide = guide_file.read()
        
        # Generate improved code using feedback
        response = litellm.completion(
            model="bedrock/converse/us.deepseek.r1-v1:0",
            messages=[{
                "role": "system",
                "content": f"""You are an expert Manim developer tasked with improving the Manim code based on user feedback.

                    Please carefully analyze both the feedback to create an improved animation:
                    1. Address each specific issue mentioned in the feedback directly
                    2. Optimize performance and visual quality based on the feedback
                    3. Ensure the animation aligns with the narrative and is visually engaging
                    4. Aim to achieve a much higher score in the next review (more than 90/100)
                    5. Improve the code based on the feedback provided.
                    6. Ensure the Manim code generated ONLY refers to the MANIM CODE GUIDE REFERENCE
                    
                    NARRATIVE TO VISUALIZE:
                    {narrative}

                    # MANIM CODE GUIDE REFERENCE:
                    {manim_code_guide}
                    """
            },
            {
                "role": "user",
                "content": f"""
                    REVIEW FEEDBACK (Score: {score}/100):
                    {review_text}

                    CURRENT CODE:
                    ```python
                    {current_code}
                    ```
            """
            }],
            temperature=0.4,
            max_tokens=8192,
        )
        
        # Extract the content from the response
        improved_code = response.choices[0].message.content
        
        # Extract code if it's wrapped in markdown code blocks
        if "```python" in improved_code and "```" in improved_code:
            code_blocks = re.findall(r'```python\n(.*?)```', improved_code, re.DOTALL)
            if code_blocks:
                improved_code = code_blocks[0]
        
        # Add comment with session id and improved version information
        improved_code = f"# Improved Manim code for session: {session_id}\n# Enhanced version based on feedback (score: {score}/100)\n\n{improved_code}"
        
        print("Successfully regenerated Manim code based on feedback")

        # Return the improved code
        return {
            "success": True,
            "improved_code": improved_code
        }
        
    except Exception as improvement_error:
        print(f"Error improving code: {str(improvement_error)}")
        return {
            "success": False,
            "error": str(improvement_error)
        }
