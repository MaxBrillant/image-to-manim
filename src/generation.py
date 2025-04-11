"""
Functions for generating script and Manim code from images
"""
import os
import re
import base64
from io import BytesIO
from PIL import Image
from litellm import completion
import litellm

from src.config import (
    DEEPINFRA_API_KEY,
    SCRIPT_PROMPT_TEMPLATE
)

# litellm._turn_on_debug()

def generate_problem_analysis(image):
    """Generate animation script from image"""
    # Convert image to base64 preserving its format
    buffered = BytesIO()
    img_format = image.format if image.format else "JPEG"
    image.save(buffered, format=img_format)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Determine the MIME type for the base64 string
    mime_type = f"image/{img_format.lower()}"
    if mime_type == "image/jpg":
        mime_type = "image/jpeg"
    
    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        
        response = litellm.completion(
            model = "deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""
                    You are a world-class mathematical educator with expertise in analysing math problems. 
                    
                    ## CRITICAL PRIORITY: MATHEMATICAL CORRECTNESS

                    MATHEMATICAL ACCURACY IS THE ABSOLUTE HIGHEST PRIORITY. Never sacrifice correctness for any reason.

                    1. **Verify every mathematical statement** before including it in your analysis
                    2. **Double-check all solutions** using first principles and standard mathematical techniques
                    3. **Do not hallucinate solutions** - if you're uncertain about any step, omit it entirely
                    4. **Only include mathematically proven facts** - no approximations or simplifications that compromise accuracy
                    5. **When analyzing the problem image**, ensure your solution matches exactly what's shown, without adding assumptions
                    
                    Analyze the mathematical problem in the provided image using the following structured approach:

                    ## 1. Initial Observation
                    Begin by carefully observing the image. Identify:
                    - The type of mathematical problem presented (geometric, algebraic, numeric pattern, etc.)
                    - All visible numbers, variables, shapes, and symbols
                    - Any missing or unknown values (often marked with question marks)
                    - The apparent goal of the problem

                    ## 2. Pattern Recognition
                    - Look for established mathematical patterns or theorems that might apply
                    - Identify relationships between numbers or geometric elements
                    - Note any sequences, proportions, or spatial arrangements that follow mathematical principles
                    - Consider classic mathematical relationships that match the visual configuration

                    ## 3. Knowledge Application
                    - Determine which mathematical principles are relevant (Pythagorean theorem, area formulas, algebraic identities, etc.)
                    - List the formulas or theorems needed to solve the problem
                    - Convert visual information into mathematical expressions where appropriate

                    ## 4. Problem Decomposition
                    - Break down complex problems into smaller, manageable components
                    - Identify if there are multiple steps or nested relationships
                    - Determine if there are hidden sub-problems that need to be solved first
                    - Create a logical sequence for addressing each component

                    ## 5. Step-by-Step Solution
                    - Work through each component methodically
                    - Show all calculations and transformations clearly
                    - Verify intermediate results when possible
                    - Maintain mathematical rigor throughout the solution process

                    ## 6. Solution Verification
                    - Check if the answer is reasonable given the context
                    - Verify that your solution satisfies all stated conditions
                    - Consider alternative approaches to confirm the result
                    - Ensure dimensional consistency and appropriate units

                    ## 7. Insight Communication
                    - Explain key insights that led to the solution
                    - Highlight any clever techniques or shortcuts used
                    - Connect the solution to broader mathematical concepts
                    - Present the final answer clearly and concisely

                    Respond with a complete analysis following this structure, making your reasoning transparent at each step.
                    """
                    ,
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
                ]
            }],
            temperature=0.4,
            max_tokens=8192,
        )
        
        # Extract the content from the response
        script = response.choices[0].message.content
        return script
        
    except Exception as e:
        print(f"Error generating problem analysis: {str(e)}")
        raise Exception(f"Failed to generate problem analysis: {str(e)}")
    

def generate_script(problem_analysis):
    """Generate script script from problem analysis"""
    

    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        
        response = litellm.completion(
            model = "deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": SCRIPT_PROMPT_TEMPLATE,
            },
            {
                "role": "user",
                "content": f"PROBLEM ANALYSIS: \n{problem_analysis}"
            }],
            temperature=0.4,
            max_tokens=8192,
        )
        
        # Extract the content from the response
        script = response.choices[0].message.content
        return script
        
    except Exception as e:
        print(f"Error generating script: {str(e)}")
        raise Exception(f"Failed to generate script: {str(e)}")

def generate_manim_code(script, session_id):
    """Generate Manim code from script"""

    os.environ["DEEPINFRA_API_KEY"] = "WfUmeoWPncZzGC2MY8oGfTEmT9RqfMjG"
    
    try:
        # Load the manim code guide
        manim_guide_path = os.path.join("resources", "manim_code_guide.txt")
        with open(manim_guide_path, "r") as guide_file:
            manim_code_guide = guide_file.read()
        
        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""
                    You are an expert Manim developer. You need to create a Manim animation that visualizes the provided script.

                    Ensure the Manim code generated ONLY refers to the MANIM CODE GUIDE REFERENCE

                    MANIM CODE GUIDE REFERENCE:
                    {manim_code_guide}
                    """
            },
            {
                "role": "user",
                "content": "SCRIPT: \n" + script
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


def regenerate_manim_code(script, previous_code, error_message, session_id):
    """Regenerate Manim code based on previous code and error message"""

    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        # Load the manim code guide
        manim_guide_path = os.path.join("resources", "manim_code_guide.txt")
        with open(manim_guide_path, "r") as guide_file:
            manim_code_guide = guide_file.read()

        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""You are an expert Manim developer. You need to fix the following Manim code that failed to render.

                    Please analyze the error message carefully and fix the Manim code to create a working animation that visualizes the script. 
                    Make sure to:
                    1. Fix any syntax errors or bugs in the code
                    2. Simplify complex animations that might be causing rendering issues
                    3. Ensure the Manim code generated ONLY refers to the MANIM CODE GUIDE REFERENCE

                    SCRIPT TO VISUALIZE:
                    {script}

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


def improve_video_from_feedback(session_id, current_code, review_text, script, score, code_path):
    """Function to improve video based on feedback reviews"""
    
    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        # Load the manim code guide
        manim_guide_path = os.path.join("resources", "manim_code_guide.txt")
        with open(manim_guide_path, "r") as guide_file:
            manim_code_guide = guide_file.read()
        
        # Generate improved code using feedback
        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""You are an expert Manim developer tasked with improving the Manim code based on user feedback.

                    Please carefully analyze both the feedback to create an improved animation:
                    1. Address each specific issue mentioned in the feedback directly
                    2. Optimize performance and visual quality based on the feedback
                    3. Ensure the animation aligns with the script and is visually engaging
                    4. Aim to achieve a much higher score in the next review (more than 90/100)
                    5. Improve the code based on the feedback provided.
                    6. Ensure the Manim code generated ONLY refers to the MANIM CODE GUIDE REFERENCE
                    
                    SCRIPT TO VISUALIZE:
                    {script}

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
