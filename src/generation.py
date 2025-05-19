"""
Functions for generating script and Manim code from images
"""
import os
import re
import base64
from io import BytesIO
import litellm

from src.config import (
    DEEPINFRA_API_KEY,
    SCRIPT_PROMPT_TEMPLATE,
    MANIM_CODE_GUIDE,
    MANIM_GUIDELINES,
    VIDEO_QUALITY_STANDARDS
)

# litellm._turn_on_debug()

def generate_problem_analysis(image):
    """Generate problem analysis from image"""
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
                    - Connect the solution to broader mathematical concepts
                    - Present the final answer clearly and concisely

                    ## CRITICAL PRIORITY: MATHEMATICAL CORRECTNESS

                    MATHEMATICAL ACCURACY IS THE ABSOLUTE HIGHEST PRIORITY. Never sacrifice correctness for any reason.

                    1. **Verify every mathematical statement** before including it in your analysis
                    2. **Double-check all solutions** using first principles and standard mathematical techniques
                    3. **Do not hallucinate solutions** - if you're uncertain about any step, omit it entirely
                    4. **Only include mathematically proven facts** - no approximations or simplifications that compromise accuracy
                    5. **When analyzing the problem image**, ensure your solution matches exactly what's shown, without adding assumptions

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
        analysis = response.choices[0].message.content
        return analysis
        
    except Exception as e:
        print(f"Error generating problem analysis: {str(e)}")
        raise Exception(f"Failed to generate problem analysis: {str(e)}")
    

def generate_script(problem_analysis):
    """Generate script from problem analysis"""
    

    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        
        response = litellm.completion(
            model = "deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": SCRIPT_PROMPT_TEMPLATE
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
    """Generate Manim code from script with strict adherence to timing, positioning and element management"""

    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""You are a specialized Manim expert whose sole focus is translating mathematical animation scripts into reliable, visually impressive Manim code. Your expertise in mathematics visualization and Manim implementation allows you to create code that is both efficient and precisely aligned with the script provided to you.

            ## ABSOLUTE PRIORITIES

            1. STRICT SCRIPT ADHERENCE
                - Follow script timing EXACTLY as specified (e.g. "at 0:30", "for 2 seconds")
                - Implement precise element positioning using the 3x3 grid system
                - Never exceed 3 elements on screen simultaneously
                - Track and manage element lifecycles (entry/exit times)
                - Maintain exact element spacing (15% minimum separation)

            2. EXACT TIMESTAMP IMPLEMENTATION
               - Every single timestamp in the script MUST be implemented precisely
               - When script says "at 0:30", the animation MUST start at exactly 30 seconds
               - When script says "for 2 seconds", the animation MUST last exactly 2 seconds
               - Add self.wait() with exact durations to reach specified timestamps
               - Track cumulative time to ensure perfect timing alignment
               - Never approximate or round timestamps
               - Document every timestamp in code comments

            3. POSITIONING AND ELEMENT MANAGEMENT
               - Implement precise element positioning using the 3x3 grid system
               - Never exceed 3 elements on screen simultaneously
               - Track and manage element lifecycles (entry/exit times)
               - Maintain exact element spacing (15% minimum separation)

            4. ELEMENT POSITIONING SYSTEM
               - Use the 9-region grid system (TOP_LEFT, TOP_CENTER, etc.)
               - Specify exact coordinates for each element
               - Maintain minimum 15% spacing between elements
               - Handle z-index for overlapping regions
               - Track element sizes (small: 10-15%, medium: 15-30%, large: 30-50%)

            5. ELEMENT LIFECYCLE
               - Track creation time for each element
               - Implement specified exit animations
               - Ensure all elements are cleared by end
               - Handle element transitions and transformations
               - Maintain element count limit

            6. STRICTLY ADHERE TO VIDEO QUALITY STANDARDS
               - Your primary goal is to create animations that meet or exceed our established video quality standards
               - Every animation decision must align with these standards
               - Quality standards take precedence over implementation convenience
               - See the VIDEO QUALITY STANDARDS REFERENCE for specific requirements

            ## VIDEO QUALITY STANDARDS REFERENCE:
            {VIDEO_QUALITY_STANDARDS}

            ## MANIM CODE GENERATION GUIDELINES:
            {MANIM_GUIDELINES}

            ## MANIM CODE GUIDE REFERENCE:
            {MANIM_CODE_GUIDE}
            """
            },
            {
                "role": "user",
                "content": "## SCRIPT: \n" + script
            }],
            temperature=0.2,  # Lower temperature for more reliable output
            max_tokens=8192,
        )
        
        # Extract the content from the response
        manim_code = response.choices[0].message.content
        
        # Extract code if it's wrapped in markdown code blocks
        if "```python" in manim_code and "```" in manim_code:
            import re
            code_blocks = re.findall(r'```python\n(.*?)```', manim_code, re.DOTALL)
            if code_blocks:
                manim_code = '\n'.join(code_blocks)  # Join multiple code blocks if present
        
        # Remove any remaining markdown formatting
        manim_code = re.sub(r'```\s*$', '', manim_code)  # Remove trailing markdown markers
        
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

        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""You are a world-class Manim debugging specialist with extensive experience fixing rendering errors in mathematical animations. Your task is to repair the broken Manim code provided, ensuring it renders correctly while preserving the intended educational content.

                    ## ERROR ANALYSIS PROTOCOL

                    1. **Identify Error Pattern**:
                    - Parse the exact error message and line number
                    - Determine if the error is: syntax error, object reference issue, animation conflict, memory/performance issue, or mathematical incorrectness

                    2. **Root Cause Assessment**:
                    - Examine the surrounding code context of the error location
                    - Check for incorrect object references or undefined variables
                    - Identify any animations that might be conflicting or improperly sequenced
                    - Look for memory-intensive operations that could be causing performance issues

                    ## SYSTEMATIC REPAIR STRATEGY

                    1. **Fix Critical Errors First**:
                    - Address syntax errors and undefined references immediately
                    - Ensure all required imports are present
                    - Verify class structure and method implementation follow Manim v0.17.0 conventions

                    2. **Simplification Hierarchy** (implement in this order):
                    - Reduce number of simultaneous animations without losing conceptual clarity
                    - Replace complex custom objects with simpler built-in alternatives
                    - Decrease resolution or detail of mathematical objects where appropriate
                    - Optimize animation transitions and timing to reduce computational load

                    3. **Animation Sequence Optimization**:
                    - Ensure each object is created before being animated
                    - Verify all animations have valid mobjects
                    - Separate complex animation sequences into simpler steps
                    - Add appropriate wait times between critical steps (0.5-1s)
                    - Fade out elements that are no longer needed

                    4. **Common Manim Error Solutions**:
                    - For "No mobjects found in AnimationGroup": Ensure all animation methods have valid mobjects
                    - For "AttributeError: 'NoneType' object has no attribute": Check if objects exist before referencing
                    - For "ValueError: need at least one array to concatenate": Verify VMobjects have points defined
                    - For memory issues: Reduce object count, simplify geometries, or split into multiple scenes
                    - For LaTeX errors: Simplify mathematical expressions and verify syntax

                    5. **Code Structure Verification**:
                    - Ensure proper class definition and inheritance
                    - Verify construct method implementation
                    - Check for proper scene setup with appropriate background color
                    - Validate all color definitions match the provided semantic color system


                    ## ABSOLUTE PRIORITIES

                    1. STRICT SCRIPT ADHERENCE
                        - Follow script timing EXACTLY as specified (e.g. "at 0:30", "for 2 seconds")
                        - Implement precise element positioning using the 3x3 grid system
                        - Never exceed 3 elements on screen simultaneously
                        - Track and manage element lifecycles (entry/exit times)
                        - Maintain exact element spacing (15% minimum separation)

                    2. EXACT TIMESTAMP IMPLEMENTATION
                    - Every single timestamp in the script MUST be implemented precisely
                    - When script says "at 0:30", the animation MUST start at exactly 30 seconds
                    - When script says "for 2 seconds", the animation MUST last exactly 2 seconds
                    - Add self.wait() with exact durations to reach specified timestamps
                    - Track cumulative time to ensure perfect timing alignment
                    - Never approximate or round timestamps
                    - Document every timestamp in code comments

                    3. POSITIONING AND ELEMENT MANAGEMENT
                    - Implement precise element positioning using the 3x3 grid system
                    - Never exceed 3 elements on screen simultaneously
                    - Track and manage element lifecycles (entry/exit times)
                    - Maintain exact element spacing (15% minimum separation)

                    4. ELEMENT POSITIONING SYSTEM
                    - Use the 9-region grid system (TOP_LEFT, TOP_CENTER, etc.)
                    - Specify exact coordinates for each element
                    - Maintain minimum 15% spacing between elements
                    - Handle z-index for overlapping regions
                    - Track element sizes (small: 10-15%, medium: 15-30%, large: 30-50%)

                    5. ELEMENT LIFECYCLE
                    - Track creation time for each element
                    - Implement specified exit animations
                    - Ensure all elements are cleared by end
                    - Handle element transitions and transformations
                    - Maintain element count limit

                    ## YOUR TASK

                    Analyze the provided error message carefully and rewrite the failed Manim code to create a working animation that visualizes the provided script. Focus on stability and reliability - an elegant working animation is better than a complex broken one.

                    ERROR MESSAGE:
                    {error_message[:5000]}

                    SCRIPT TO VISUALIZE:
                    {script}

                    ## VIDEO QUALITY STANDARDS REFERENCE:
                    {VIDEO_QUALITY_STANDARDS}

                    # MANIM CODE GUIDE REFERENCE:
                    {MANIM_CODE_GUIDE}
                    """
            }, {
                "role": "user",
                "content": f"""
                    ## FAILED MANIM CODE:
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
        
        # Generate improved code using feedback
        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""You are a Manim expert whose singular focus is to analyze feedback on mathematical animations and rewrite the entire code to address the specific issues mentioned. Your goal is to generate completely new code that directly solves all problems identified in the feedback.

                    ## FEEDBACK UNDERSTANDING PROCESS

                    1. READ THE FEEDBACK CAREFULLY, identifying each specific issue mentioned:
                       - Extract every concrete problem mentioned in the feedback
                       - Note exactly what aspects of the animation were criticized
                       - Pay special attention to mathematical accuracy issues
                       
                    2. For each specific issue identified:
                       - Determine precisely what code changes would fix this issue
                       - Prioritize issues affecting mathematical correctness or rendering

                    ## CODE REWRITING APPROACH

                    1. COMPLETELY REWRITE THE CODE from scratch to address the feedback
                       - Do not simply make minor adjustments to the original code
                       - Create new implementation that solves all identified issues
                       - Ensure the new code follows the MANIM CODE GUIDE REFERENCE exactly

                    2. For each specific feedback point:
                       - Implement a direct solution to that exact problem
                       - Write a brief comment explaining how your code addresses this feedback point
                       - Verify your solution fully resolves the issue

                       
                    ## ABSOLUTE PRIORITIES

                    1. STRICT SCRIPT ADHERENCE
                        - Follow script timing EXACTLY as specified (e.g. "at 0:30", "for 2 seconds")
                        - Implement precise element positioning using the 3x3 grid system
                        - Never exceed 3 elements on screen simultaneously
                        - Track and manage element lifecycles (entry/exit times)
                        - Maintain exact element spacing (15% minimum separation)

                    2. EXACT TIMESTAMP IMPLEMENTATION
                    - Every single timestamp in the script MUST be implemented precisely
                    - When script says "at 0:30", the animation MUST start at exactly 30 seconds
                    - When script says "for 2 seconds", the animation MUST last exactly 2 seconds
                    - Add self.wait() with exact durations to reach specified timestamps
                    - Track cumulative time to ensure perfect timing alignment
                    - Never approximate or round timestamps
                    - Document every timestamp in code comments

                    3. POSITIONING AND ELEMENT MANAGEMENT
                    - Implement precise element positioning using the 3x3 grid system
                    - Never exceed 3 elements on screen simultaneously
                    - Track and manage element lifecycles (entry/exit times)
                    - Maintain exact element spacing (15% minimum separation)

                    4. ELEMENT POSITIONING SYSTEM
                    - Use the 9-region grid system (TOP_LEFT, TOP_CENTER, etc.)
                    - Specify exact coordinates for each element
                    - Maintain minimum 15% spacing between elements
                    - Handle z-index for overlapping regions
                    - Track element sizes (small: 10-15%, medium: 15-30%, large: 30-50%)

                    5. ELEMENT LIFECYCLE
                    - Track creation time for each element
                    - Implement specified exit animations
                    - Ensure all elements are cleared by end
                    - Handle element transitions and transformations
                    - Maintain element count limit

                    6. STRICTLY ADHERE TO VIDEO QUALITY STANDARDS
                    - Your primary goal is to create animations that meet or exceed our established video quality standards
                    - Every animation decision must align with these standards
                    - Quality standards take precedence over implementation convenience
                    - See the VIDEO QUALITY STANDARDS REFERENCE for specific requirements


                    ## VERIFICATION

                    Before submitting the new code, verify:
                    - Each specific piece of feedback has been directly addressed
                    - The code fully implements the script while fixing all issues
                    - All mathematical concepts are accurately represented
                    - The code strictly follows the MANIM CODE GUIDE REFERENCE

                    
                    REVIEW FEEDBACK (Score: {score}/100):
                    {review_text}

                    SCRIPT TO VISUALIZE:
                    {script}

                    ## VIDEO QUALITY STANDARDS REFERENCE:
                    {VIDEO_QUALITY_STANDARDS}

                    # MANIM CODE GENERATION GUIDELINES:
                    {MANIM_GUIDELINES}

                    # MANIM CODE GUIDE REFERENCE:
                    {MANIM_CODE_GUIDE}
                    """
            }, {
                "role": "user",
                "content": f"""
                    ## MANIM CODE TO IMPROVE:
                    ```python
                    {current_code}
                    ```"""
            }],
            temperature=0.2,
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
