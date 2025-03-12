# Image to Manim - Educational Video Generator

This API takes an image of a problem or question as input and automatically generates an educational animation explaining the solution using the 3Blue1Brown Manim library.

## Overview

The pipeline follows this structure:

1. **Generate narrative script** - Using the input image to create an educational narrative using AWS Bedrock (Claude 3.5 Sonnet)
2. **Generate Manim code** - Creating animation code from the narrative using AWS Bedrock
3. **Store assets** - Saving all generated content to Supabase storage
4. **Render** - Producing the final educational video using Modal cloud computing

## Requirements

- Python 3.8+
- Flask
- Manim Animation Engine
- AWS Bedrock API access (Claude 3.5 Sonnet model)
- Supabase account (for storage and database)
- Modal account (for cloud rendering)

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
AWS_REGION_NAME=us-west-2  # Or your preferred AWS region
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Supabase Configuration

1. Create a new Supabase project
2. Create a storage bucket named `manim-generator`
3. Create a table named `manim_projects` with the following schema:
   ```sql
   create table manim_projects (
     id uuid primary key,
     status text,
     narrative text,
     narrative_url text,
     code_url text,
     image_url text,
     video_url text,
     render_error text,
     created_at timestamp with time zone default now()
   );
   ```
4. Set appropriate storage policies to allow public access to generated files

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

### Local Development

1. First, deploy the Modal renderer (if not already deployed):

   ```
   modal deploy modal_renderer.py
   ```

2. Start the API server with:
   ```
   python app.py
   ```

The server will run at `http://localhost:5000`

### Using Docker

You can also run the application using Docker:

1. Build the Docker image:

   ```
   docker build -t image-to-manim .
   ```

2. Run the container:
   ```
   docker run -p 8000:8000 --env-file .env image-to-manim
   ```

The server will run at `http://localhost:8000`

Note: When running in Docker, the Modal renderer still needs to be deployed separately.

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

### Deployment

The project includes configuration for deployment on Render.com:

1. Connect your GitHub repository to Render.com
2. Configure the required environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Deploy the service

The `render.yaml` file includes the necessary configuration for a web service using the Docker environment.

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

Main endpoint that initiates the processing pipeline. This endpoint handles the entire workflow:

1. Uploads the image to Supabase storage
2. Generates a narrative script using AWS Bedrock (Claude 3.5 Sonnet)
3. Generates Manim code based on the narrative
4. Stores all assets in Supabase
5. Automatically queues the video rendering job on Modal

**Request:**

- Form data with an image file (key: 'image')

**Response:**

```json
{
  "session_id": "unique_session_id",
  "narrative": "Generated narrative text",
  "narrative_url": "https://supabase-url/storage/v1/object/public/manim-generator/session_id/narrative.txt",
  "code_url": "https://supabase-url/storage/v1/object/public/manim-generator/session_id/scene.py",
  "image_url": "https://supabase-url/storage/v1/object/public/manim-generator/session_id/original.jpg",
  "video_url": "https://supabase-url/storage/v1/object/public/manim-generator/session_id/video.mp4",
  "status": "render_complete",
  "message": "Processing complete - video has been rendered and is available."
}
```

If the Modal rendering job cannot be queued, the response will include:

```json
{
  "session_id": "unique_session_id",
  "narrative": "Generated narrative text",
  "narrative_url": "https://supabase-url/storage/v1/object/public/manim-generator/session_id/narrative.txt",
  "code_url": "https://supabase-url/storage/v1/object/public/manim-generator/session_id/scene.py",
  "image_url": "https://supabase-url/storage/v1/object/public/manim-generator/session_id/original.jpg",
  "status": "code_generated",
  "message": "Code generation complete, but video rendering could not be queued.",
  "error": "Error message"
}
```

## Example Usage

### Using cURL

Process an image:

```bash
curl -X POST -F "image=@/path/to/your/image.jpg" http://localhost:5000/process-image
```

### Using Python Requests

```python
import requests

# Process image
with open('path/to/image.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/process-image', files=files)

# Get the results
result = response.json()
session_id = result['session_id']
video_url = result.get('video_url')
narrative = result['narrative']

print(f"Video available at: {video_url}")
```

## Workflow

1. Submit an image to the `/process-image` endpoint
2. The system automatically:
   - Generates a narrative script using AWS Bedrock (Claude 3.5 Sonnet)
   - Creates Manim code based on the narrative
   - Stores all assets in Supabase
   - Queues a rendering job on Modal
3. Receive a response with URLs to all generated assets, including the video (if rendering was successful)

## Output Structure

All outputs are stored in Supabase storage under the `manim-generator` bucket:

- `<session_id>/original.jpg` - The original input image
- `<session_id>/narrative.txt` - The generated narrative script
- `<session_id>/scene.py` - The generated Manim code
- `<session_id>/video.mp4` - The rendered video

Project metadata is stored in the `manim_projects` table in Supabase.

## Architecture

```
┌─────────────┐     ┌───────────────┐     ┌───────────────┐
│ Flask API   │────▶│ AWS Bedrock   │────▶│ Supabase      │
│ (app.py)    │     │ (Claude 3.5)  │     │ (Storage/DB)  │
└─────────────┘     └───────────────┘     └───────────────┘
       │                                          │
       │                                          │
       ▼                                          ▼
┌─────────────┐                         ┌───────────────┐
│ Modal       │◀────────────────────────│ Generated     │
│ (Rendering) │                         │ Assets        │
└─────────────┘                         └───────────────┘
       │
       │
       ▼
┌─────────────┐
│ Final Video │
└─────────────┘
```
