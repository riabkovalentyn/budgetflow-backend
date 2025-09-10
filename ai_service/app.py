from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os
import json
from typing import List, Optional

app = FastAPI()


class Tx(BaseModel):
    type: str
    amount: float
    category: str
    description: Optional[str] = ""
    created_at: Optional[str] = None


class AdviceIn(BaseModel):
    transactions: List[Tx]
    prompt: Optional[str] = ""


@app.post("/advice")
def advice(body: AdviceIn):
    api_key = os.getenv("OPENAI_API_KEY", "")
    provider = os.getenv("AI_PROVIDER", "openai")
    if provider != "openai" or not api_key:
        return {"advice": "AI disabled"}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        system = (
            "You are a financial assistant. Analyze transactions and give 3-5 helpful, concise tips."
        )
        content = json.dumps(body.dict())
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": content},
            ],
            temperature=0.4,
        )
        text = completion.choices[0].message.content
        return {"advice": text}
    except Exception:
        return {"advice": "AI error"}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    api_key = os.getenv("OPENAI_API_KEY", "")
    provider = os.getenv("AI_PROVIDER", "openai")
    if provider != "openai" or not api_key:
        return {"text": "AI disabled"}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        data = await audio.read()
        from io import BytesIO
        f = BytesIO(data)
        f.name = audio.filename or "audio.wav"
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )
        text = getattr(result, "text", "")
        return {"text": text}
    except Exception:
        return {"text": "AI error"}
