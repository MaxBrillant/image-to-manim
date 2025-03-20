"""
Functions for reviewing generated videos
"""
import re
import requests
from io import BytesIO
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY

def review_video(video_url, narrative):
    """Review the video and provide feedback with scoring"""
    try:
        print(f"Starting video review for: {video_url}")

        # Download the video file into a variable
        response = requests.get(video_url, stream=True)
        video_content = BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                video_content.write(chunk)
        video_content.seek(0)  # Reset buffer position to the start
        
        # Initialize the Gemini API client
        client = genai.Client(
            api_key=GEMINI_API_KEY,
        )
        
        review_prompt = f"""
        You are an expert animation critic with a keen eye for detail. Review this educational animation video that was created.

        Evaluate the animation with special focus on visual element positioning and timing:
        1. Element positioning (Check for overlapping elements, out-of-bounds items, or poor spacing)
        2. Timing and synchronization (Analyze transitions, element appearance/disappearance timing)
        3. Visual clarity (How well does it communicate concepts?)
        4. Educational value (How effectively does it teach the topic?)
        5. Overall animation quality (How smooth and professional is it?)

        Pay extra attention to:
        - Elements that overlap or collide with each other
        - Text or objects that go beyond screen boundaries
        - Poorly timed transitions or animations
        - Inconsistent spacing between elements
        - Animation elements that appear too quickly or slowly

        Provide:
        1. A numerical score out of 100 (format exactly as "SCORE: XX/100").
        2. At least 2 specific strengths of the animation.
        3. Between 5 to 10 specific areas for improvement with actionable suggestions, focusing especially on positioning and timing issues.
        4. Detailed reasoning for each point of feedback.
        
        Your review should be strict and analyze each technical detail.
        """

        # Make the API call to review the video
        response_text = ""

        for chunk in client.models.generate_content_stream(
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
                temperature=0.4,
                max_output_tokens=8192,
                response_mime_type="text/plain",
            )
        ):
            print(chunk.text, end="")
            response_text += chunk.text

        review_text = response_text
        print("Video review completed successfully")
        
        # Extract score from the review
        score_match = re.search(r"SCORE:\s*(\d+)/100", review_text)
        score = int(score_match.group(1)) if score_match else 0
        
        # Return the review details
        review_result = {
            "score": score,
            "review": review_text,
            "needs_improvement": score < 95  # Consider scores below 95 as needing improvement
        }
        
        return review_result
        
    except Exception as e:
        print(f"Error reviewing video: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            "score": 0,
            "review": f"Error reviewing video: {str(e)}",
            "needs_improvement": False  # Default to not regenerating if we can't review
        }
