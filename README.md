# Image to Manim - Educational Video Generator

Transforms images of math problems into educational animations using the Manim library.

## Overview

1. **Process image** to analyze the math problem (deepinfra/meta-llama/Llama-4-Maverick-17B)
2. **Generate animation script** for the educational explanation (deepinfra/meta-llama/Llama-4-Maverick-17B)
3. **Generate visual elements** with precise positioning and timing
4. **Generate video** with Manim animations using cloud rendering
5. **Improve video** quality with automated feedback (Google Gemini)

## Requirements

- Python 3.8+
- deepinfra API access
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
   DEEPINFRA_API_KEY=your_deepinfra_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GEMINI_API_KEY=your_gemini_key
   ```

3. Deploy Modal renderer:

   ```
   modal deploy src/render/modal_renderer.py
   ```

4. Run the app:
   ```
   python -m src.app
   ```

## Supabase Setup

1. Create storage bucket: `manim-generator`
2. Create table:
   ```sql
   create table manim_projects (
     id uuid primary key,
     status text,
     problem_analysis text,
     script_url text,
     visuals_url text,
     code_url text,
     image_url text,
     video_url text,
     created_at timestamp with time zone default now()
   );
   ```

## API Usage

```bash
# Process an image
curl -X POST -F "image=@/path/to/image.jpg" http://localhost:5000/process-image

# Generate script
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}' \
  http://localhost:5000/generate-script

# Generate visual elements
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}' \
  http://localhost:5000/generate-visuals

# Generate video (optional quality parameter: low, medium, high)
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "video_quality": "medium"}' \
  http://localhost:5000/generate-video

# Improve video
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}' \
  http://localhost:5000/improve-video

# Health check
curl http://localhost:5000/health
```

## Docker

```bash
docker build -t image-to-manim .
docker run -p 5000:5000 --env-file .env image-to-manim
```

## Key Components

- `src/app.py`: Main Flask API with modular endpoints
- `src/generation/`:
  - `problem_analysis.py`: Image analysis and math problem understanding
  - `script.py`: Educational script generation
  - `visuals.py`: Visual elements and storyboard generation
  - `manim_code.py`: Manim animation code generation
  - `review.py`: Video quality analysis and improvement
- `src/render/`:
  - `modal_renderer.py`: Modal-based GPU rendering
  - `render.py`: Rendering coordination
- `frontend/index.html`: Interactive UI with step-by-step processing
