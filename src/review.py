"""
Functions for reviewing generated videos with strict and honest feedback
"""
import re
import requests
import time
from io import BytesIO
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY

def review_video(video_url):
    """
    Review the video and provide structured feedback with scoring
    
    Args:
        video_url (str): URL to the video file to be reviewed
        
    Returns:
        dict: Contains score (int), categorized issues (dict), and overall review (str)
    """
    MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB limit
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
                raise ValueError(f"Video size ({content_length/1024/1024:.2f}MB) exceeds maximum allowed size (50MB)")
            
            video_content = BytesIO()
            downloaded_size = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded_size += len(chunk)
                    if downloaded_size > MAX_VIDEO_SIZE:
                        raise ValueError(f"Video download size exceeded maximum allowed size (50MB)")
                    video_content.write(chunk)
            
            if downloaded_size == 0:
                raise ValueError("Downloaded video is empty")
                
            video_content.seek(0)  # Reset buffer position to the start
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error downloading video: {str(e)}")
        
        print(f"Video download completed ({downloaded_size/1024/1024:.2f}MB in {time.time()-start_time:.2f}s)")
        
        # Initialize the Gemini API client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Optimized review prompt with clear structure and evaluation criteria
        review_prompt = """
        You are a senior animation reviewer specializing in Manim-based mathematical animations. Perform a strict technical evaluation of this animation video.
        
        # EVALUATION RUBRIC (100 points total):
        
        ## Visual Clarity (25 points)
        - Clear visual hierarchy and focus
        - Appropriate text size and readability
        - Proper spacing between elements
        - Mathematical notation accuracy
        
        ## Technical Execution (25 points)  
        - Elements properly positioned within frame
        - No objects cut off or outside boundaries
        - Consistent spacing and alignment
        - Appropriate scale of elements

        ## Animation Timing (25 points)
        - Appropriate animation speed
        - Proper transition timing
        - Sufficient pause duration for comprehension
        - Synchronized animations when needed
        
        ## Educational Effectiveness (25 points)
        - Logical progression of concepts
        - Appropriate emphasis on key points
        - Visual reinforcement of verbal concepts
        - Coherent mathematical storytelling
        
        # SCORING CRITERIA:
        - 90-100: Excellent (Minor improvements only)
        - 75-89: Good (Several areas need refinement)
        - 60-74: Average (Significant improvements needed)
        - Below 60: Poor (Major revisions required)
        
        # KNOWN ANIMATION ISSUES TO CHECK:
        - Overlapping elements that obscure each other
        - Objects moving too quickly to follow
        - Text appearing too briefly to read
        - Camera movements that are too rapid
        - Mathematical notation errors or inconsistencies
        - Incorrect animation timing that breaks understanding
        - Poor contrast between elements and background
        - Elements positioned beyond the visible frame
        
        # YOUR REVIEW MUST INCLUDE:
        
        1. SCORE: XX/100 (Provide an exact numerical score)
        
        2. CRITICAL ISSUES: (Must be fixed - prevent comprehension)
           - List each critical issue with specific timestamp and description
           - Provide specific fix recommendation for each
        
        3. MAJOR ISSUES: (Should be fixed - hinder quality)
           - List each major issue with specific timestamp and description
           - Provide specific fix recommendation for each
        
        4. MINOR ISSUES: (Could be fixed - would enhance quality)
           - List each minor issue with specific timestamp and description
           - Provide specific fix recommendation for each
        
        5. SUMMARY: Brief overall assessment and prioritized improvements
        
        Be extremely strict and thorough in your assessment. The animation must meet professional educational standards. Your honest, critical feedback is essential.
        """
        
        api_start_time = time.time()
        print("Sending video to Gemini API for review...")
        
        # Make the API call to review the video with timeout handling
        try:
            response_text = ""
            stream_generator = client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(
                                data=video_content.read(),
                                mime_type="video/mp4",
                            ),
                            types.Part.from_text(text=review_prompt),
                        ],
                    ),
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Lower temperature for more consistent evaluation
                    max_output_tokens=8192,
                    response_mime_type="text/plain",
                )
            )
            
            for chunk in stream_generator:
                # Check if API call timeout exceeded
                if time.time() - api_start_time > API_TIMEOUT:
                    raise TimeoutError("API review took too long to complete")
                
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    response_text += chunk.text
                    
            review_text = response_text
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
            "needs_improvement": score < 85,  # Consider scores below 85 as needing improvement
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

def extract_issues(review_text, section_header):
    """
    Extract issues from a specific section of the review text
    
    Args:
        review_text (str): The full review text
        section_header (str): The section to extract issues from
        
    Returns:
        list: Extracted issues from the section
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

def next_section_pattern(current_section):
    """
    Create regex pattern for the next section header based on the current one
    
    Args:
        current_section (str): Current section header
        
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
