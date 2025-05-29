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
                "content": f"""
<context>
You are a Manim debugging specialist working with version 0.17.0. Your expertise lies in identifying and fixing rendering errors in mathematical animations while preserving their educational value. You have access to the original code that failed and its error message.

Background: Manim is a Python library for creating mathematical animations. Common issues include syntax errors, object reference problems, animation conflicts, and memory issues.
</context>

<task>
Analyze the provided error message and failed code, then generate a fixed version that:
1. Resolves the technical issues
2. Maintains the original educational intent
3. Follows Manim best practices
4. Ensures reliable execution
</task>

<format>
Return only the complete fixed Python code that resolves the error, wrapped in a Python code block. Do not include any explanations, analysis, or additional text.

Example response format:
```python
from manim import *

class MyScene(Scene):
    def construct(self):
        # Your fixed code here
        pass
```
</format>

IMPORTANT:
1. ONLY and ALWAYS refer to the MANIM_CODE_GUIDE
2. Generate ONLY complete Python code
3. No explanations outside the code
4. Include all necessary imports
5. Add detailed comments
6. Ensure code is complete and error-free
7. Maintain the original educational intent

<error_message>
{error_message[:5000]}
</error_message>

<manim_code_guide_reference>
{MANIM_CODE_GUIDE}
</manim_code_guide_reference>
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
