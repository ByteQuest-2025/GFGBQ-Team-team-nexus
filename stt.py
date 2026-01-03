import os
import tempfile

try:
    import whisper
    HAS_WHISPER = True
except Exception:
    HAS_WHISPER = False


def transcribe_audio(file_path):
    """Transcribe audio at file_path using Whisper if available.

    Returns: (transcript: str, segments: list)
    segments is a list of dicts with keys 'start','end','text' when available.
    If audio is empty/noisy or whisper not installed, returns ('',[]).
    """
    if not os.path.exists(file_path):
        return "", []

    size = os.path.getsize(file_path)
    if size < 2048:
        # Very small file - likely silence / empty
        return "", []

    if HAS_WHISPER:
        model = whisper.load_model("tiny")
        # model.transcribe returns dict with 'text' and 'segments'
        result = model.transcribe(file_path)
        transcript = result.get("text", "").strip()
        segments = result.get("segments", []) or []
        # Ensure segments have consistent keys
        normalized = []
        for s in segments:
            normalized.append({
                "start": s.get("start", 0),
                "end": s.get("end", 0),
                "text": s.get("text", "").strip(),
            })
        return transcript, normalized
    else:
        # Fallback: Whisper not installed. Return empty transcript so caller
        # can provide transcript-only input. This keeps the demo stable.
        return "", []
