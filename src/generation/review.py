"""
Functions for reviewing generated videos with strict and honest feedback
"""
import re
import requests
import time
from io import BytesIO
from typing import Dict, List, Union, Optional
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY, VIDEO_QUALITY_STANDARDS

def review_video(video_url: str) -> Dict[str, Union[int, Dict[str, List[str]], str, bool, float]]:
    """
    Review the video and provide structured feedback with scoring
    
    Args:
        video_url: URL to the video file to be reviewed
        
    Returns:
        Dict containing:
            score: int (0-100)
            issues: Dict with critical, major, minor issues as List[str]
            review: str (full review text)
            needs_improvement: bool
            review_time: float
    """
    MAX_VIDEO_SIZE = 20 * 1024 * 1024  # 20MB limit for Gemini
    DOWNLOAD_TIMEOUT = 60  # 60 seconds timeout for download
    API_TIMEOUT = 90  # 90 seconds timeout for API call
    
    try:
        print(f"Starting video review for: {video_url}")
        start_time = time.time()
        
        # Download the video file with size limit and timeout
        try:
            response = requests.get(
                video_url, 
                stream=True, 
                timeout=DOWNLOAD_TIMEOUT,
                headers={'User-Agent': 'ManimReviewAgent/1.0'}
            )
            response.raise_for_status()  # Raise exception for 4XX/5XX status codes
            
            content_length = int(response.headers.get('content-length', 0))
            if content_length > MAX_VIDEO_SIZE:
                raise ValueError(f"Video size ({content_length/1024/1024:.2f}MB) exceeds maximum allowed size (20MB)")
            
            video_content = BytesIO()
            downloaded_size = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded_size += len(chunk)
                    if downloaded_size > MAX_VIDEO_SIZE:
                        raise ValueError(f"Video download size exceeded maximum allowed size (20MB)")
                    video_content.write(chunk)
            
            if downloaded_size == 0:
                raise ValueError("Downloaded video is empty")
                
            video_content.seek(0)  # Reset buffer position to the start
            video_bytes = video_content.read()  # Read entire content into memory
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error downloading video: {str(e)}")
        
        print(f"Video download completed ({downloaded_size/1024/1024:.2f}MB in {time.time()-start_time:.2f}s)")
        
        # Initialize the Gemini API client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Optimized review prompt with clear structure and evaluation criteria
        review_prompt = f"""
        <role>
        You are a senior animation reviewer specializing in mathematical educational content. You combine 3Blue1Brown's philosophy of mathematical visualization with established video quality standards to ensure animations effectively communicate mathematical concepts while maintaining professional quality.
        </role>

        <context>
        These animations serve as educational tools for teaching mathematical concepts. They target students and educators who need clear, intuitive visualizations of complex mathematical ideas. The animations must balance technical accuracy with intuitive understanding, making abstract concepts concrete through visual metaphors and progressive concept building.

        Our goal is to create animations that:
        - Make mathematical concepts visually intuitive
        - Build understanding through progressive disclosure
        - Maintain professional production quality
        - Meet established educational standards
        </context>

        <examples>
        Example of Well-Scored Animation (95/100):
        - Clear progressive build-up of concept
        - Smooth, well-timed transitions
        - Mathematical notation appears with perfect timing
        - Visual metaphors clearly connect to concepts
        - Professional rendering quality
        - Appropriate pauses for comprehension

        Example of Poor Animation (45/100):
        - Concepts introduced too quickly
        - Jerky transitions between steps
        - Mathematical notation hard to read
        - Unclear visual relationships
        - Elements move off screen
        - No time for viewer comprehension
        </examples>

        <evaluation_criteria>

        Primary Evaluation Areas:

        1. VIDEO QUALITY STANDARDS COMPLIANCE
        - Every animation must strictly adhere to our established quality standards
        - Reference and apply the standards defined in VIDEO_QUALITY_STANDARDS
        - Flag any deviations from these standards as critical issues
        - Consider quality standards as non-negotiable requirements

        2. MATHEMATICAL VISUALIZATION EFFECTIVENESS
        - Evaluate how well the animation reveals mathematical understanding
        - Assess the clarity and insight of visual explanations
        - Check for proper progressive disclosure of concepts
        - Verify effective use of visual metaphors

        Review Process Steps:
        1. First watch: Overall flow and mathematical clarity
        2. Second watch: Technical quality and timing
        3. Third watch: Detailed issue identification
        4. Final analysis: Score assignment and recommendations

        Evaluation Rubric (100 points total):
        
        </evaluation_criteria>

        <scoring_rubric>
        Mathematical Insight (25 points)
        - Reveals core mathematical relationships visually (5 pts)
        - Shows why concepts work, not just what they are (5 pts)
        - Builds intuition before formality (5 pts)
        - Creates meaningful "aha moments" (5 pts)
        - Uses transformations to demonstrate structure (5 pts)
        
        Visual Quality (25 points)
        - Clear visual hierarchy and focus (5 pts)
        - Proper contrast and visibility (5 pts)
        - Clean, professional rendering (5 pts)
        - Consistent visual style (5 pts)
        - Mathematical notation accuracy (5 pts)
        
        Technical Execution (25 points)
        - Elements properly positioned and scaled (5 pts)
        - No objects cut off or misaligned (5 pts)
        - Smooth, artifact-free animations (5 pts)
        - Proper frame composition (5 pts)
        - Camera movements well-executed (5 pts)
        
        Animation Flow (25 points)
        - Appropriate animation speed and timing (5 pts)
        - Meaningful transitions that aid understanding (5 pts)
        - Strategic pauses for insight absorption (5 pts)
        - Synchronized animations when needed (5 pts)
        - Progressive build-up of complexity (5 pts)
        </scoring_rubric>

        <validation_criteria>
        Score Validation Requirements:
        90-100: Must have evidence of excellence in all categories
        75-89: May have minor issues but core mathematical communication intact
        60-74: Multiple significant issues affecting comprehension
        Below 60: Major failures in multiple critical areas

        Issue Documentation Requirements:
        - Timestamps must be in MM:SS format
        - Each issue must include specific evidence
        - Fix recommendations must be actionable
        - Critical issues must explain comprehension impact

        Edge Cases:
        - Partially visible elements: Note exact time and screen position
        - Unclear timestamps: Use range format (MM:SS-MM:SS)
        - Technical glitches: Document frequency and impact
        - Unreadable text: Measure minimum on-screen duration
        </validation_criteria>

        <output_format>
        Your review must follow this exact structure:

        SCORE: [0-100]/100
        [Include point breakdown for each category]

        CRITICAL ISSUES:
        - [MM:SS] Issue description
          Impact: [How it prevents comprehension]
          Fix: [Specific recommendation]

        MAJOR ISSUES:
        - [MM:SS] Issue description
          Impact: [How it hinders quality]
          Fix: [Specific recommendation]

        MINOR ISSUES:
        - [MM:SS] Issue description
          Impact: [How it affects enhancement]
          Fix: [Specific recommendation]

        ANALYSIS STEPS:
        1. [Key observations from first watch]
        2. [Technical quality assessment]
        3. [Detailed issues found]
        4. [Reasoning for final score]

        SUMMARY:
        [Overall assessment]
        [Top 3 priority improvements]
        [Impact on mathematical understanding]
        </output_format>

        <quality_standards>
        {VIDEO_QUALITY_STANDARDS}
        </quality_standards>
        """
        
        api_start_time = time.time()
        print("Sending video to Gemini API for review...")
        
        # Make the API call to review the video with timeout handling
        try:
            response = client.models.generate_content(
                model='models/gemini-2.0-flash',
                contents=types.Content(
                    parts=[
                        types.Part(
                            inline_data=types.Blob(
                                data=video_bytes,
                                mime_type='video/mp4'
                            )
                        ),
                        types.Part(text=review_prompt)
                    ]
                )
            )
            
            review_text = response.text
            print("\nVideo review completed successfully")
            
        except Exception as api_error:
            raise ValueError(f"Error during API review: {str(api_error)}")
        
        # Extract and validate score from the review
        score_match = re.search(r"SCORE:\s*(\d+)/100", review_text)
        if not score_match:
            print("Warning: Could not find score in review text, using fallback extraction")
            # Fallback to any number that looks like a score
            score_fallback = re.search(r"(\d{1,3})\s*(?:/|out of)\s*100", review_text)
            score = int(score_fallback.group(1)) if score_fallback else 50
        else:
            score = int(score_match.group(1))
        
        # Validate score is within range
        score = max(0, min(score, 100))
        
        # Extract categorized issues using regex
        issues = {
            "critical": extract_issues(review_text, "CRITICAL ISSUES"),
            "major": extract_issues(review_text, "MAJOR ISSUES"),
            "minor": extract_issues(review_text, "MINOR ISSUES")
        }
        
        # Return structured review details
        review_result = {
            "score": score,
            "issues": issues,
            "review": review_text,
            "needs_improvement": score < 90,  # Consider scores below 90 as needing improvement
            "review_time": time.time() - start_time
        }
        
        return review_result
        
    except Exception as e:
        print(f"Error reviewing video: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            "score": 0,
            "issues": {
                "critical": [f"Review process failed: {str(e)}"],
                "major": [],
                "minor": []
            },
            "review": f"Error reviewing video: {str(e)}",
            "needs_improvement": True  # Assume needs improvement if review failed
        }

def extract_issues(review_text: str, section_header: str) -> List[str]:
    """
    Extract issues from a specific section of the review text
    
    Args:
        review_text: The full review text
        section_header: The section to extract issues from
        
    Returns:
        List[str]: Extracted issues from the section
    """
    # Find the section in the review
    pattern = rf"{section_header}:(.*?)(?:(?:{next_section_pattern(section_header)})|$)"
    section_match = re.search(pattern, review_text, re.DOTALL | re.IGNORECASE)
    
    if not section_match:
        return []
    
    section_text = section_match.group(1).strip()
    
    # Extract individual issues (items starting with dash or bullet)
    issues = []
    for line in section_text.split('\n'):
        line = line.strip()
        # Match lines that start with -, *, or bullet-like patterns
        if re.match(r'^[-*•⋅◦⦿⁃▪▫➤➢➣➪➫➬➭➮➯]', line):
            clean_line = re.sub(r'^[-*•⋅◦⦿⁃▪▫➤➢➣➪➫➬➭➮➯]\s*', '', line).strip()
            if clean_line:  # Only add non-empty lines
                issues.append(clean_line)
    
    return issues

def next_section_pattern(current_section: str) -> str:
    """
    Create regex pattern for the next section header based on the current one
    
    Args:
        current_section: Current section header
        
    Returns:
        str: Regex pattern for the next likely section
    """
    sections = ["CRITICAL ISSUES", "MAJOR ISSUES", "MINOR ISSUES", "SUMMARY"]
    try:
        current_index = sections.index(current_section)
        if current_index < len(sections) - 1:
            return sections[current_index + 1]
        else:
            return "END OF REVIEW"
    except ValueError:
        return "|".join(sections)  # If section not found, return all possible next sections
