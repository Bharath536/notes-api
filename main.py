from fastapi import FastAPI, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import shutil

app = FastAPI()


# Base Model
class BaseNote(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=5, max_length=500)


# Input Model
class NoteCreate(BaseNote):
    id: int = Field(..., gt=0)


# Output Model
class NoteOut(BaseNote):
    id: int


# Fake Database
fake_notes_db = []


# Helper Function
def note_not_found():
    return HTTPException(
        status_code=404,
        detail="Note not found",
        headers={"X-Error": "Invalid Note ID"}
    )


# Custom Exception
class NegativeNumberException(Exception):
    pass


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request, exc: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content={
            "message": "Negative numbers are not allowed."
        }
    )


@app.get("/")
def home():
    return {"message": "Notes API"}


# Create Note
@app.post("/notes/", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def add_note(note: NoteCreate):

    for existing_note in fake_notes_db:
        if existing_note.id == note.id:
            raise HTTPException(
                status_code=400,
                detail="Note ID already exists"
            )

    fake_notes_db.append(note)
    return note


# Get Notes
@app.get("/notes/", response_model=list[NoteOut])
def get_notes(title: str = None, limit: int = 100):

    if limit < 0:
        raise NegativeNumberException()

    if title is None:
        return fake_notes_db[:limit]

    result = []

    for note in fake_notes_db:
        if note.title.lower() == title.lower():
            result.append(note)

    return result


# Update Note
@app.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, updated_note: NoteCreate):

    for index, note in enumerate(fake_notes_db):
        if note.id == note_id:
            fake_notes_db[index] = updated_note
            return updated_note

    raise note_not_found()


# Delete Note
@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):

    for index, note in enumerate(fake_notes_db):
        if note.id == note_id:
            fake_notes_db.pop(index)
            return

    raise note_not_found()


# Upload File
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type
    }