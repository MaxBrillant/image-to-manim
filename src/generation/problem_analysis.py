import os
import re
import base64
from io import BytesIO
import litellm
from PIL import Image
from typing import Optional

from src.config import (
    DEEPINFRA_API_KEY
)

def generate_problem_analysis(image: Image.Image) -> str:
    """
    Generate problem analysis from image
    
    Args:
        image: PIL Image object containing the math problem
        
    Returns:
        str: Structured analysis of the mathematical problem
    """
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
