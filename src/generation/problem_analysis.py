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
                    <context>
                    You are a world-class mathematical educator with expertise in analysing math problems. Your analysis will be used to generate educational content that makes complex mathematical concepts accessible while maintaining rigorous accuracy.

                    Purpose:
                    - Generate clear, rigorous mathematical analyses
                    - Make complex concepts accessible to learners
                    - Highlight key insights and learning opportunities
                    - Provide foundation for educational content generation
                    </context>

                    <task>
                    Analyze the mathematical problem in the provided image using a structured approach that maintains mathematical rigor while ensuring clarity and educational value.
                    </task>

                    <format>
                    Your analysis must follow this exact structure:

                    # Initial Observation
                    Problem Type: [geometric/algebraic/numeric/etc.]
                    Visual Elements:
                    - [List all numbers, variables, shapes, symbols]
                    - [List any missing or unknown values]
                    Goal: [Clear statement of the problem objective]

                    # Pattern Recognition
                    Identified Patterns:
                    - [Pattern 1 with explanation]
                    - [Pattern 2 with explanation]
                    Mathematical Relationships:
                    - [List relevant relationships]

                    # Knowledge Application
                    Relevant Principles:
                    - [Principle 1]: [Brief explanation]
                    - [Principle 2]: [Brief explanation]
                    Required Formulas:
                    - [Formula 1]
                    - [Formula 2]

                    # Problem Decomposition
                    Components:
                    1. [Component 1]
                       - Prerequisites: [List any]
                       - Approach: [Brief description]
                    2. [Component 2]
                       - Prerequisites: [List any]
                       - Approach: [Brief description]

                    # Step-by-Step Solution
                    1. [Step 1]
                       - Work: [Show calculations]
                       - Result: [Intermediate result]
                    2. [Step 2]
                       - Work: [Show calculations]
                       - Result: [Intermediate result]

                    # Solution Verification
                    Checks Performed:
                    - [Check 1]: [Result]
                    - [Check 2]: [Result]
                    Alternative Approaches:
                    - [Approach 1]: [Brief description]

                    # Key Insights
                    Mathematical Insights:
                    - [Insight 1]
                    - [Insight 2]
                    Educational Value:
                    - [Learning point 1]
                    - [Learning point 2]

                    </format>

                    <examples>
                    Here's an example of a well-structured analysis:

                    Initial Observation
                    Problem Type: Geometric
                    Visual Elements:
                    - Right triangle with sides 3, 4, and unknown hypotenuse
                    - Right angle marked with square symbol
                    Goal: Find the length of the hypotenuse
                    
                    Pattern Recognition
                    Identified Patterns:
                    - Right triangle with known legs
                    - Standard Pythagorean theorem application
                    [...]
                    </examples>

                    <constraints>
                    1. Error Handling Requirements:
                       - Explicitly state ambiguous elements
                       - List all possible interpretations
                       - Explain uncertainty barriers
                       - Provide analysis for each valid interpretation

                    2. Quality Validation Requirements:
                       - All mathematical statements must be proven
                       - All calculations must be double-checked
                       - No assumptions beyond given information
                       - All steps must be clearly explained
                       - Format must strictly follow template
                       - All uncertainties must be acknowledged

                    3. Critical Priority - Mathematical Correctness:
                       - Verify every mathematical statement
                       - Double-check all solutions using first principles
                       - Do not hallucinate solutions - omit uncertain steps
                       - Only include mathematically proven facts
                       - Solutions must match exactly what's shown in the image
                    </constraints>
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
