from io import BytesIO, StringIO
from fastapi import FastAPI, HTTPException, UploadFile
from pdfminer.high_level import extract_text_to_fp, extract_text
from dotenv import load_dotenv, find_dotenv

from services.llm_summarize import llm_summarize

# Load the ENV variables
load_dotenv(find_dotenv())

# Constants
max_size = 150000

# Create app server
app = FastAPI()

# Routes
@app.get("/")
def read_root():
    return { "Hello": "World" }


@app.post("/api/summarize")
async def summarize_script(file: UploadFile):

    # Check file size
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum limit.")
    
    with BytesIO(content) as file_buffer:
        text = extract_text(file_buffer)

    # text = await extract_text(contents)
    response = await llm_summarize(text)
    return response