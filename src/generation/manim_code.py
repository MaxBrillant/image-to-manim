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
    
    # Prepare improvements section if improvements are provided
    improvements_section = f"""
    <context>
    The following feedback has been provided for improving the animation:
    {improvements}
    </context>

    <success_criteria>
    1. All feedback points are addressed completely
    2. Mathematical accuracy is maintained or improved
    3. Visual clarity is enhanced
    4. Code quality meets standards
    5. Animation timing is optimized
    </success_criteria>

    <analysis_process>
    1. Feedback Analysis:
        - Extract each distinct issue
        - Categorize by type (mathematical, visual, technical)
        - Identify dependencies between issues
        - Prioritize critical problems

    2. Solution Planning:
        - Map each issue to specific code sections
        - Determine required modifications
        - Plan testing approach
        - Consider impact on other components

    3. Implementation Strategy:
        - Address fundamental issues first
        - Maintain existing functionality
        - Follow code style guidelines
        - Document all changes
    </analysis_process>

    <validation_checklist>
    [ ] Each feedback point has a corresponding solution
    [ ] Mathematical representations are accurate
    [ ] Visual elements follow style guide
    [ ] Code meets quality standards
    [ ] Performance impact is acceptable
    [ ] Changes are properly documented
    </validation_checklist>

    <verification_steps>
    1. Code Review:
        - Compare against original feedback
        - Verify mathematical accuracy
        - Check animation timing
        - Validate style compliance

    2. Quality Assurance:
        - Test each modified component
        - Verify scene transitions
        - Check resource usage
        - Validate error handling

    3. Final Verification:
        - Run complete animation
        - Compare with requirements
        - Verify documentation
        - Check for regressions
    </verification_steps>
    """ if improvements else ""
    
    try:
        response = litellm.completion(
            model="deepinfra/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{
                "role": "system",
                "content": f"""
                <context>
                You are an expert Manim developer specializing in educational animations. Your task is to generate complete, production-ready Manim code from visual elements specifications.
                </context>

                <success_criteria>
                1. Code compiles and runs without errors
                2. Animations match visual specifications exactly
                3. Mathematical concepts are accurately represented
                4. Timing and synchronization are precise
                5. Each element or object appears and disappears at the specified time
                6. All objects have been successfully cleared from the screen at the appropriate time
                7. Code is well-documented and maintainable
                </success_criteria>

                <implementation_guide>
                ## Phase 1: Planning and Setup
                1. Analyze the visual elements specification
                2. Break down complex animations into steps
                3. Plan object lifecycles and transitions
                4. Identify potential mathematical challenges

                ## Phase 2: Implementation
                - Create descriptive variable names reflecting mathematical meaning
                - Add detailed comments for complex logic
                - Focus on reliability before visual complexity
                - Follow test-driven development approach:
                    1. Start with basic shapes/positions
                    2. Add animations incrementally
                    3. Verify each step before proceeding
                    4. Clear all objects/elements at the provided disappearance time
                    5. In the end, all objects have to be cleared from the screen

                ## Phase 3: Error Prevention
                - Common Manim Errors to Avoid:
                    * Never reference objects before creation
                    * Verify AnimationGroup mobject validity
                    * Ensure VMobjects have defined points
                    * Use appropriate coordinate systems
                    * Validate latex expression formatting

                ## Phase 4: Quality Control
                - Self-Validation Steps:
                    1. Check all mathematical representations
                    2. Verify timing synchronization
                    3. Confirm smooth transitions
                    4. Test edge cases
                    5. Validate against specifications
                    4. Clear all objects/elements at the provided disappearance time
                    5. In the end, all objects have to be cleared from the screen
                </implementation_guide>

                <technical_requirements>
                1. Scene Structure:
                    - Create ManimScene class as main controller
                    - Implement separate classes per storyboard scene
                    - Match initial states exactly
                    - Follow keyframe sequence order
                    - Clear all objects/elements at the provided disappearance time
                </technical_requirements>

                <output_format>
                1. Code Structure:
                    ```python
                    # Required imports
                    from manim import *

                    GRID_POSITIONS = {{
                        "top_left": (-4, 2, 0),
                        "top_center": (0, 2, 0),
                        "top_right": (4, 2, 0),
                        "middle_left": (-4, 0, 0),
                        "middle_center": (0, 0, 0),
                        "middle_right": (4, 0, 0),
                        "bottom_left": (-4, -2, 0),
                        "bottom_center": (0, -2, 0),
                        "bottom_right": (4, -2, 0),
                        "custom_position_1": ...,
                        "custom_position_2": ...
                    }}

                    class MainScene(Scene):
                        def construct(self):
                            # Initialize shared variables and objects
                            self.setup_scene()
                            
                            # Execute animation sequence
                            self.play_sequence()
                        
                        def setup_scene(self):
                            pass
                            
                        def play_sequence(self):
                            # Example sequence structure:
                            # 1. Introduction
                            self.play_introduction()
                            
                            # 2. Main content
                            self.play_main_content()
                            
                            # 3. Conclusion
                            self.play_conclusion()
                        
                        def play_introduction(self):
                            pass
                            
                        def play_main_content(self):
                            pass
                            
                        def play_conclusion(self):
                            pass
                    ```

                2. Documentation Requirements:
                    - File-level docstring explaining purpose and usage
                    - Class-level docstring describing the overall animation structure
                    - Method-level docstrings for each animation sequence
                    - Inline comments explaining complex logic or mathematical concepts
                    - TODO comments for potential optimizations
                    
                3. Scene Organization:
                    - Single MainScene class controls entire animation flow
                    - Modular methods for different animation sequences
                    - Clear separation of setup and animation logic
                    - Proper timing and transitions between sequences
                    - Shared state management through class attributes
                    - VERY IMPORTANT: If a grid position is being used by another element,
                    remove or clear the old object/element before positioning the new object/element
                </output_format>

                <examples>
                # Example 1: Good Implementation
                ```python
                class ProperImplementation(Scene):
                    # Demonstrates correct implementation of a mathematical concept animation
                    # following all best practices and requirements.

                    def construct(self):
                        # 1. Proper setup and positioning
                        equation = MathTex("f(x) = x^2").move_to(GRID_POSITIONS["top_center"])
                        graph = FunctionGraph(lambda x: x**2, x_range=[-2, 2])
                        graph.move_to(GRID_POSITIONS["middle_center"])
                        
                        # 2. Clear animation sequence with proper timing
                        self.play(Write(equation))
                        self.wait()  # Allow time for comprehension
                        
                        # 3. Smooth transition and transformation
                        self.play(Create(graph))
                        self.wait()
                        
                        # 4. Proper cleanup
                        self.play(
                            FadeOut(equation),
                            FadeOut(graph)
                        )
                ```

                # Example 2: Poor Implementation (Anti-Pattern)
                ```python
                class IncorrectImplementation(Scene):
                    def construct(self):
                        # WRONG: No docstring, unclear purpose
                        
                        # WRONG: Hard-coded positions instead of GRID_POSITIONS
                        eq = MathTex("f(x)=x^2").move_to([1, 1, 0])
                        
                        # WRONG: Instant addition without animation
                        self.add(eq)
                        
                        # WRONG: No wait time for audience comprehension
                        g = FunctionGraph(lambda x: x**2)
                        self.play(Create(g))
                        
                        # WRONG: Objects left on screen, no cleanup
                        # WRONG: No proper timing management
                ```

                # Example 3: Complex Animation Sequence
                ```python
                class ComplexAnimationExample(Scene):
                    # Demonstrates proper handling of multiple objects,
                    # transitions, and timing management.
                    
                    def construct(self):
                        # 1. Initialize objects with clear naming
                        initial_equation = MathTex("a^2 + b^2").move_to(GRID_POSITIONS["top_left"])
                        middle_equation = MathTex("= c^2").move_to(GRID_POSITIONS["top_center"])
                        triangle = Triangle().scale(2).move_to(GRID_POSITIONS["middle_center"])
                        
                        # 2. Staged animation sequence
                        self.play(Write(initial_equation))
                        self.wait(0.5)
                        
                        self.play(
                            Write(middle_equation),
                            Create(triangle)
                        )
                        self.wait()
                        
                        # 3. Complex transformation
                        self.play(
                            triangle.animate.set_color(BLUE),
                            initial_equation.animate.set_color(RED),
                            middle_equation.animate.set_color(RED)
                        )
                        self.wait()
                        
                        # 4. Proper cleanup in reverse order
                        self.play(
                            FadeOut(triangle),
                            FadeOut(middle_equation),
                            FadeOut(initial_equation)
                        )
                ```
                </examples>

                <multishot_patterns>
                # Common Animation Patterns and Their Usage

                1. Object Creation and Transformation:
                ```python
                # Pattern 1: Smooth object introduction
                self.play(Write(text))  # For text/equations
                self.play(Create(shape))  # For geometric shapes
                
                # Pattern 2: Object transformation
                self.play(Transform(initial_obj, target_obj))
                
                # Pattern 3: Multiple simultaneous animations
                self.play(
                    Write(text),
                    Create(shape),
                    run_time=2
                )
                ```

                2. Position Management:
                ```python
                # Pattern 1: Grid-based positioning
                obj1.move_to(GRID_POSITIONS["top_left"])
                obj2.move_to(GRID_POSITIONS["bottom_right"])
                
                # Pattern 2: Relative positioning
                obj2.next_to(obj1, RIGHT)
                obj3.beside(obj2, DOWN)
                ```

                3. Cleanup Patterns:
                ```python
                # Pattern 1: Individual cleanup
                self.play(FadeOut(obj1))
                
                # Pattern 2: Group cleanup
                self.play(*[FadeOut(obj) for obj in [obj1, obj2, obj3]])
                
                # Pattern 3: Scene cleanup with timing
                self.play(
                    *[FadeOut(mob) for mob in self.mobjects],
                    run_time=1.5
                )
                ```

                4. Mathematical Animations:
                ```python
                # Pattern 1: Equation writing
                equation = MathTex("E = mc^2")
                self.play(Write(equation))
                
                # Pattern 2: Step-by-step reveal
                steps = VGroup(
                    MathTex("a^2"),
                    MathTex("+"),
                    MathTex("b^2"),
                    MathTex("="),
                    MathTex("c^2")
                ).arrange(RIGHT)
                for step in steps:
                    self.play(FadeIn(step))
                ```
                </multishot_patterns>

                <validation_checklist>
                # Core Requirements
                - [ ] All imports are present and necessary
                - [ ] Scene hierarchy matches specification
                - [ ] Grid positions are accurately mapped
                - [ ] Animations follow timing requirements
                - [ ] Mathematical representations are correct

                # Pattern Compliance
                - [ ] Uses demonstrated creation/transformation patterns
                - [ ] Follows position management patterns
                - [ ] Implements proper cleanup patterns
                - [ ] Mathematical animations follow best practices

                # Object Lifecycle
                - [ ] Clear all objects/elements at the provided disappearance time
                - [ ] In the end, all objects have to be cleared from the screen
                - [ ] Element lifecycles are properly managed
                - [ ] Elements are positioned using the grid positions provided in GRID_POSITIONS

                # Code Quality
                - [ ] Code is well-documented
                - [ ] Error handling is implemented
                - [ ] Follows good implementation examples
                - [ ] Avoids demonstrated anti-patterns
                </validation_checklist>

                IMPORTANT:
                1. ONLY and ALWAYS refer to the MANIM_CODE_GUIDE
                2. Generate ONLY complete Python code
                3. No explanations outside the code
                4. Include all necessary imports
                5. Add detailed comments
                6. Ensure code is complete and error-free

                # If improvements are requested, follow this process:
                {improvements_section if improvements else ""}

                # Reference guide for all implementations:                
                <manim_code_guide>
                <description>
                Standard reference for Manim code implementation, covering all aspects from basic structure to advanced techniques.
                </description>
                <content>
                {MANIM_CODE_GUIDE}
                </content>
                </manim_code_guide>
                """
            },
            {
                "role": "user",
                "content": "## VISUAL ELEMENTS: \n" + visual_elements
            }],
            temperature=0.2,  # Lower temperature for more reliable output
            max_tokens=8192,
        )
        
        
        manim_code = response.choices[0].message.content
        # Extract content after </think>
        if "</think>" in manim_code:
            manim_code = response.choices[0].message.content.split("</think>")[1].strip()
        
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
