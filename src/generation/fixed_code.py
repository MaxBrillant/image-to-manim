import os
import re
import litellm

from src.config import (
    DEEPINFRA_API_KEY,
    MANIM_CODE_GUIDE
)

def fix_manim_code(previous_code: str, error_message: str, session_id: str) -> str:
    """
    Regenerate Manim code based on previous code and error message
    
    Args:
        previous_code: Previous Manim code that failed
        error_message: Error message from the failed render
        session_id: Session identifier for tracking
        
    Returns:
        str: Fixed Manim code
    """
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

                    ## YOUR TASK

                    Analyze the provided error message carefully and rewrite the failed Manim code to create a working animation. Focus on stability and reliability - an elegant working animation is better than a complex broken one.

                    ERROR MESSAGE:
                    {error_message[:5000]}

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
