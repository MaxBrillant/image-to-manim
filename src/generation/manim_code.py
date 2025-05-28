import os
import re
import litellm
from typing import Optional

from src.config import (
    DEEPINFRA_API_KEY,
    MANIM_CODE_GUIDE,
)

def generate_manim_code(visual_elements: str, improvements: Optional[str] = None, session_id: str = None) -> str:
    """
    Generate Manim code from visual element specifications with strict adherence to timing, positioning and element management
    
    Args:
        visual_elements: Visual element specifications to implement
        improvements: Optional feedback for improvements
        session_id: Session identifier for tracking
        
    Returns:
        str: Generated Manim code
    """
    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""You are an expert Manim developer specializing in educational animations.
                Generate complete, production-ready Manim code from the provided visual elements specifications.

                Follow this systematic approach to generate high-quality Manim code:

                1. **IMPLEMENTATION PHASE**
                - Create clearly named variables that reflect their mathematical meaning
                - Add comments explaining complex parts of the implementation
                - Focus on reliability first, visual complexity second

                2. **ERROR PREVENTION**
                - Avoid common Manim errors:
                    - Never reference objects before they're created
                    - Ensure all AnimationGroups contain valid mobjects
                    - Verify all VMobjects have points defined
                    - Use appropriate coordinate systems
                    - Ensure latex expressions are properly formatted

                3. OUTPUT REQUIREMENTS (VERY IMPORTANT):
                    1. ONLY and ALWAYS refer to the MANIM_CODE_GUIDE
                    2. Generate ONLY the complete Python code for the Manim animation. Do NOT include explanations, discussions, or descriptions outside the code
                    3. Include all necessary imports at the top of the file
                    4. Add helpful comments explaining complex parts of the implementation
                    5. Ensure the code is complete, runnable, and error-free

                4. STRICT VISUALS ADHERENCE (VERY IMPORTANT):
                
                ## Scene Structure Implementation
                - Create a ManimScene class that calls all the other scenes
                - Create a separate class for each storyboard scene
                - Implement exact durations using wait() calls
                - Match initial state setup precisely
                - Follow key frame sequence in order
                
                ## Grid System Translation
                - Map 3×3 grid positions to Manim coordinates:
                    * top-left: (-4, 2, 0)     top-center: (0, 2, 0)     top-right: (4, 2, 0)
                    * middle-left: (-4, 0, 0)   middle-center: (0, 0, 0)   middle-right: (4, 0, 0)
                    * bottom-left: (-4, -2, 0)  bottom-center: (0, -2, 0)  bottom-right: (4, -2, 0)
                - Scale elements according to specified size percentages
                - Maintain minimum 15% spacing between elements
                
                ## Element Lifecycle Management
                - Create precise entry animations as specified
                - Implement all transitions between key frames
                - Execute exit animations exactly as described
                - Track element states throughout the scene
                
                ## Timing and Synchronization
                - Use AnimationGroups for simultaneous animations
                - Implement precise wait times between key frames
                - Ensure smooth flow between scenes
                - Match storyboard timing specifications exactly

                {"" if not improvements else f"""IMPROVEMENTS TO CONSIDER FROM REVIEW:
                    {improvements}

                    ## FEEDBACK UNDERSTANDING PROCESS

                        1. READ THE FEEDBACK CAREFULLY, identifying each specific issue mentioned:
                        - Extract every concrete problem mentioned in the feedback
                        - Note exactly what aspects of the animation were criticized
                        - Pay special attention to mathematical accuracy issues
                        
                        2. For each specific issue identified:
                        - Determine precisely what code changes would fix this issue
                        - Prioritize issues affecting mathematical correctness or rendering
                        
                    ## VERIFICATION

                        Before submitting the new code, verify:
                        - Each specific piece of feedback has been directly addressed
                        - The code fully implements the script while fixing all issues
                        - All mathematical concepts are accurately represented
                        - The code strictly follows the MANIM CODE GUIDE REFERENCE"""}    
                
                MANIM_CODE_GUIDE:
                {MANIM_CODE_GUIDE}
                """
            },
            {
                "role": "user",
                "content": "## VISUAL ELEMENTS: \n" + visual_elements
            }],
            temperature=0.2,  # Lower temperature for more reliable output
            max_tokens=8192,
        )
        
        # Extract the content from the response
        manim_code = response.choices[0].message.content
        
        # Extract code if it's wrapped in markdown code blocks
        if "```python" in manim_code and "```" in manim_code:
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
