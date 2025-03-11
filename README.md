# Image to Manim - Educational Video Generator

This API takes an image of a problem or question as input and automatically generates an educational animation explaining the solution using the 3Blue1Brown Manim library.

## Overview

The pipeline follows this structure:

1. **Generate narrative script** - Using the input image to create an educational narrative
2. **Generate Manim code** - Creating animation code from the narrative
3. **Review/refine** - Allowing for refinement of the narrative and code
4. **Render** - Producing the final educational video

## Requirements

- Python 3.8+
- Flask
- Manim Animation Engine
- OpenRouter API key
- Modal (for cloud rendering)

## Installation

1. Clone the repository
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Manim dependencies (see [Manim documentation](https://docs.manim.community/en/stable/installation.html))
4. Install Modal:
   ```
   pip install modal
   ```

## Configuration

Set the required API keys in the `.env` file:

```
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Modal Configuration

To use Modal for cloud rendering:

1. Authenticate with Modal:

   ```
   modal token new
   ```

2. Deploy the Modal renderer:
   ```
   modal deploy modal_renderer.py
   ```

## Running the API

1. First, deploy the Modal renderer (if not already deployed):

   ```
   modal deploy modal_renderer.py
   ```

2. Start the API server with:
   ```
   python app.py
   ```

The server will run at `http://localhost:5000`

### Complete Setup Sequence

For a fresh installation, follow these steps in order:

1. Install dependencies:

   ```
   pip install -r requirements.txt
   pip install modal
   ```

2. Authenticate with Modal:

   ```
   modal token new
   ```

3. Deploy the Modal renderer:

   ```
   modal deploy modal_renderer.py
   ```

4. Start the Flask API server:
   ```
   python app.py
   ```

## API Endpoints

### 1. Health Check

```
GET /health
```

Checks if the server is running.

### 2. Process Image

```
POST /process-image
```

Main endpoint that initiates the processing pipeline.

**Request:**

- Form data with an image file (key: 'image')

**Response:**

```json
{
  "session_id": "unique_session_id",
  "narrative": "Generated narrative text",
  "narrative_path": "path/to/narrative.txt",
  "manim_code_path": "path/to/scene.py",
  "status": "processing_complete",
  "message": "Initial processing complete. You can now review and refine."
}
```

### 3. Refine Content

```
POST /refine/<session_id>
```

Updates the narrative and regenerates the code and audio.

**Request:**

```json
{
  "narrative": "Updated narrative text"
}
```

**Response:**

```json
{
  "session_id": "session_id",
  "narrative": "Updated narrative text",
  "narrative_path": "path/to/narrative.txt",
  "manim_code_path": "path/to/scene.py",
  "status": "refinement_complete",
  "message": "Refinement complete. You can now render the video."
}
```

### 4. Render Video

```
POST /render-video/<session_id>
```

Renders the final video using Manim.

**Response:**

```json
{
  "session_id": "session_id",
  "video_path": "path/to/video.mp4",
  "status": "render_complete",
  "message": "Video rendering complete."
}
```

## Example Usage

### Using cURL

1. Process an image:

```bash
curl -X POST -F "image=@/path/to/your/image.jpg" http://localhost:5000/process-image
```

2. Refine the narrative:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"narrative":"Your revised narrative text"}' http://localhost:5000/refine/<session_id>
```

3. Render the final video:

```bash
curl -X POST http://localhost:5000/render-video/<session_id>
```

### Using Python Requests

```python
import requests

# Process image
with open('path/to/image.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/process-image', files=files)

session_id = response.json()['session_id']

# Refine narrative (optional)
refined_narrative = "Your refined narrative text"
requests.post(f'http://localhost:5000/refine/{session_id}',
              json={'narrative': refined_narrative})

# Render video
requests.post(f'http://localhost:5000/render-video/{session_id}')
```

## Workflow

1. Submit an image to the `/process-image` endpoint
2. Receive a session ID and the generated narrative
3. Review the narrative and make any necessary refinements via the `/refine/<session_id>` endpoint
4. Trigger the video rendering via the `/render-video/<session_id>` endpoint
5. Access the generated video from the returned path

## Output Structure

All outputs are stored in the `outputs/<session_id>/` directory:

- `original.jpg` - The original input image
- `narrative.txt` - The generated narrative script
- `scene.py` - The generated Manim code
- Video output in the `videos/` subdirectory
