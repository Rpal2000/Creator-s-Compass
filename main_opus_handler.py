import os
import json
from google import genai
from google.genai import types
from data_models import VideoAnalysisResult  # Import Pydantic models

# --- Configuration ---
# The client automatically picks up the GEMINI_API_KEY environment variable.
client = genai.Client()
MODEL_NAME = 'gemini-2.5-flash'


def get_base_analysis_prompt(goal: str) -> str:
    """Creates the base prompt for the initial multimodal analysis."""
    # Use system instruction for role and format
    return (
        "You are an expert video producer and content quality analyst. Your task is to analyze the "
        "provided video URL/file for technical quality issues. "
        "Focus on: 1) Camera Angle/Framing, 2) Lighting Quality, 3) Audio Clarity/Noise, 4) Video Pacing/Engagement. "
        "Generate a structured JSON output that conforms exactly to the VideoAnalysisResult schema. "
        f"The user's goal is: {goal}. Be critical but constructive."
    )


def perform_video_analysis(video_uri: str, user_goal: str, reference_video_uri: str = None) -> dict:
    """
    Performs the initial Gemini analysis using the provided URIs and user goal.
    In Opus, this logic would run in the 'External Service' or 'Code' node.
    """

    # 1. Setup the initial prompt and tool configuration

    # This is a key hackathon trick: using the Pydantic schema for structured output.
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=VideoAnalysisResult,
    )

    # 2. Prepare the content parts
    contents = []

    # Add the main video content (Gemini supports YouTube URLs directly in contents)
    # NOTE: For an uploaded file, you would first use client.files.upload() and then
    # use the File object's URI here. For the hackathon, starting with a URL is faster.
    main_video_part = types.Part.from_uri(
        uri=video_uri,
        mime_type="video/mp4"  # or video/youtube, etc. Gemini often handles the URL type.
    )
    contents.append(main_video_part)

    # Handle the 'Option 3: Copy & Create' scenario by passing both videos
    if reference_video_uri and user_goal == "Option 3":
        ref_video_part = types.Part.from_uri(
            uri=reference_video_uri,
            mime_type="video/mp4"
        )
        contents.append(ref_video_part)
        base_prompt = (
            f"Compare the FIRST video (User's upload) with the SECOND video (Reference/Goal). "
            f"{get_base_analysis_prompt(user_goal)}"
        )
    else:
        base_prompt = get_base_analysis_prompt(user_goal)

    contents.append(types.Part.from_text(base_prompt))

    print(f"-> Sending request to Gemini with goal: {user_goal}")

    # 3. Call the Gemini API
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )

        # The response text will be a JSON string conforming to the Pydantic model
        return json.loads(response.text)

    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Return a standard error structure for Opus to handle
        return {"error": str(e), "message": "Failed to get analysis from Gemini."}


# --- Example of running the script in a Hackathon demo ---
if __name__ == "__main__":
    # Ensure GEMINI_API_KEY is set in your environment
    if not os.getenv("AIzaSyCj7PMtfMsDadu0opfSeoDgyuAMOh4Spw4"):
        print("FATAL: Please set the GEMINI_API_KEY environment variable.")
    else:
        # Example 1: User uploads their video (Option 2)
        print("\n=== Running Test: Option 2 (User Video Analysis) ===")
        # NOTE: Replace with a public video URL for testing!
        USER_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Use a valid link

        analysis_result = perform_video_analysis(
            video_uri=USER_VIDEO_URL,
            user_goal="Option 2: Creator needs to identify problems in their video and get solutions."
        )

        # This is the JSON object passed to the next Opus node
        print("\n--- Raw JSON Output for Opus ---")
        print(json.dumps(analysis_result, indent=2))

        # Opus logic: check for Human Review flag
        if analysis_result.get('overall_score', 10) < 5:
            print("\n!!! ACTION REQUIRED: Score < 5. Triggering Opus Human Review Node.")
        else:
            print("\nAnalysis complete. Proceeding to final report generation.")