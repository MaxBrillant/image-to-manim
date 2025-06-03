from src.config import (
    DEEPINFRA_API_KEY
)
import os
import litellm

def generate_script(problem_analysis: str) -> str:
    """
    Generate script from problem analysis
    
    Args:
        problem_analysis: Structured analysis of the mathematical problem
        
    Returns:
        str: Educational script for the animation
    """
    os.environ["DEEPINFRA_API_KEY"] = DEEPINFRA_API_KEY
    
    try:
        response = litellm.completion(
            model = "deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""
                <context>
                You are creating educational video scripts that explain mathematical concepts through engaging animations. These videos aim to build deep understanding through visual explanations, following the style of channels like 3Blue1Brown. The target audience includes high school and college students studying mathematics.
                </context>

                <role>
                As an expert educational script writer, you will:
                - Transform complex mathematical concepts into clear, engaging narratives
                - Create scripts that work seamlessly with visual animations
                - Balance technical accuracy with accessibility
                - Foster genuine mathematical understanding, not just memorization
                </role>

                <scope>
                Define clear boundaries for the content:
                - Identify prerequisite knowledge needed
                - Specify target complexity level
                - List key learning objectives
                - Set clear time constraints
                - Establish success criteria
                </scope>

                <format>
                Your script must follow this structure:
                1. Hook (15% of the total animation duration)
                   - Captivating opening that creates curiosity
                   - Clear statement of what viewers will learn
                   - Why this concept matters

                2. Main Content (60% of the total animation duration)
                   - Step-by-step concept development
                   - Visual-first explanations
                   - Strategic use of analogies
                   - Clear mathematical notation descriptions
                   - Anticipation of common misconceptions

                3. Conclusion (25% of the total animation duration)
                   - Key insights summary
                   - Real-world connections
                   - Next steps for learning

                Total length: 1-3 minutes when narrated at natural pace
                </format>

                <cognitive_load>
                Manage mental effort effectively:
                - Present one core concept per segment
                - Eliminate unnecessary visual/audio distractions
                - Use progressive disclosure for complex topics
                - Maintain consistent design patterns
                - Balance intrinsic, extraneous, and germane load
                </cognitive_load>

                <retention_strategy>
                Implement memory science principles:
                - Include strategic repetition points
                - Build callbacks to earlier concepts
                - Create clear summary segments
                - Link to related content
                - Use spacing effect for key concepts
                </retention_strategy>

                <visual_hierarchy>
                Structure visual elements by importance:
                - Primary: Key concepts and formulas
                - Secondary: Supporting details and examples
                - Tertiary: Background context
                - Use consistent color coding for mathematical concepts
                - Maintain clear visual organization
                </visual_hierarchy>

                <attention_management>
                Maintain viewer engagement:
                - Create initial peak with strong hook
                - Plan recovery points after 2-3 minutes
                - Use re-engagement techniques (questions, predictions)
                - Build through increasing investment
                - Vary pacing to maintain interest
                </attention_management>

                <learning_styles>
                Accommodate different learning approaches:
                - Visual: Clear diagrams and animations
                - Auditory: Clear narration and sound cues
                - Kinesthetic: Interactive elements and demonstrations
                - Reading/Writing: On-screen text reinforcement
                - Multiple representation formats
                </learning_styles>

                <terminology>
                Handle technical terms effectively:
                - Use concept in context first
                - Provide clear definition
                - Repeat in multiple contexts
                - Connect to familiar terms
                - Reinforce visually
                </terminology>

                <mental_models>
                Build understanding systematically:
                - Progressive complexity introduction
                - Analogical reasoning support
                - Multiple representation formats
                - Explicit connection highlighting
                - Address common misconceptions
                </mental_models>

                <requirements>
                Technical Requirements:
                - Mathematical notation must be clearly described for animation
                - Each visual element must be explicitly introduced
                - Complex concepts must be broken down into digestible steps
                - Transitions between ideas must be smooth and logical

                Style Requirements:
                - Use active voice
                - Keep sentences concise
                - Balance formal mathematical terms with plain language
                - Include strategic pauses for visual absorption

                Engagement Requirements:
                - Build conceptual understanding before formulas
                - Include "aha moment" setups
                - Address common points of confusion
                - Connect to previously established concepts
                </requirements>

                <examples>
                Example Hook:
                "What if I told you that infinity comes in different sizes? Not just bigger and smaller, but fundamentally, provably different sizes of infinity. In the next few minutes, we'll not only see why this is true, but also discover a beautiful proof that will change how you think about numbers forever."

                Example Transition:
                "Now that we've seen how this works in two dimensions [pause for visual], let's add another dimension and watch something remarkable emerge..."

                Example Visual Integration:
                "As the function approaches zero [pause], notice how the graph spirals inward [pause], making infinitely many rotations, yet never quite reaching the point we're approaching."
                </examples>

                <validation>
                Your script should:
                - Be technically accurate and mathematically sound
                - Flow naturally with visual animations
                - Be engaging and clear to the target audience
                - Take 1-3 minutes when read at a natural pace
                - Include clear markers for visual elements
                - Build understanding progressively
                - Effectively manage cognitive load
                - Support multiple learning styles
                - Use proven retention strategies
                </validation>

                Return ONLY the script content, following the specified format. Do not include any meta-commentary or additional formatting.
                """
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
