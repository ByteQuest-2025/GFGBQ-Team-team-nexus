from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os

from stt import transcribe_audio
from fraud_detector import analyze_transcript
from utils import save_upload_file_to_temp

app = FastAPI(title="Scam Call Detector Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze-call")
async def analyze_call(
    request: Request, file: UploadFile = File(None), transcript: str = Form(None)
):
    # Support application/json with {"transcript": "..."}
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        body = await request.json()
        transcript = body.get("transcript")
        file = None

    if file:
        tmp_path = save_upload_file_to_temp(file)
        transcript_text, segments = transcribe_audio(tmp_path)
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    elif transcript:
        transcript_text = transcript
        segments = []
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide an audio file or a transcript in the request",
        )

    result = analyze_transcript(transcript_text, segments)

    response = {
        "transcript": transcript_text,
        "risk_score": result.get("score", 0),
        "risk_level": result.get("level", "LOW"),
        "reasons": result.get("reasons", []),
    }
    if result.get("timestamps"):
        response["timestamps"] = result.get("timestamps")

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
