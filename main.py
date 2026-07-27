from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Note(BaseModel):
    id: int
    title: str
    content: str

fake_notes_db = []

@app.get("/")
def home():
    return {"message": "Notes API"}

@app.post("/notes/")
def add_note(note: Note):
    fake_notes_db.append(note)
    return {
        "message": "Note added successfully",
        "note": note
    }

@app.get("/notes/")
def get_notes(title: str = None):
    if title is None:
        return fake_notes_db

    result = []

    for note in fake_notes_db:
        if note.title.lower() == title.lower():
            result.append(note)

    return result

@app.put("/notes/{note_id}")
def update_note(note_id: int, updated_note: Note):
    for index, note in enumerate(fake_notes_db):
        if note.id == note_id:
            fake_notes_db[index] = updated_note
            return {
                "message": "Note updated successfully",
                "note": updated_note
            }

    raise HTTPException(status_code=404, detail="Note not found")
@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    for index, note in enumerate(fake_notes_db):
        if note.id == note_id:
            deleted_note = fake_notes_db.pop(index)
            return {
                "message": "Note deleted successfully",
                "note": deleted_note
            }

    raise HTTPException(status_code=404, detail="Note not found")
