# Image to Manim - Educational Video Generator

Transforms images of problems or questions into educational animations using the Manim library.

## Overview

1. **Generate narrative** from image (AWS Bedrock/Claude)
2. **Generate code** from narrative (AWS Bedrock/Deepseek)
3. **Render** animation using Modal cloud computing
4. **Review** video quality and improve if needed (Google Gemini)

## Requirements

- Python 3.8+
- AWS Bedrock API access
- Google Gemini API access
- Supabase account
- Modal account

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   pip install modal
   ```

2. Set up environment variables in `.env`:

   ```
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GEMINI_API_KEY=your_gemini_key
   ```

3. Deploy Modal renderer:

   ```
   modal deploy modal_renderer.py
   ```

4. Run the app:
   ```
   python app.py
   ```

## Supabase Setup

1. Create storage bucket: `manim-generator`
2. Create table:
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

## API Usage

```bash
# Process an image
curl -X POST -F "image=@/path/to/image.jpg" http://localhost:5000/process-image

# Health check
curl http://localhost:5000/health
```

### Response Format

```json
{
  "session_id": "uuid",
  "video_url": "https://...",
  "status": "review_complete",
  "review": {
    "score": 95
  }
}
```

## Docker

```bash
docker build -t image-to-manim .
docker run -p 8000:8000 --env-file .env image-to-manim
```

## Key Components

- `app.py`: Main Flask API
- `src/modal_renderer.py`: Modal-based GPU rendering
- `src/generation.py`: Narrative and code generation
- `src/review.py`: Video quality analysis
