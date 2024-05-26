from pydantic import BaseModel

class User(BaseModel):
    userId: str
    user_id: int

class ReadingData(BaseModel):
    year: int
    month: int
    book_count: int
    chapter_count: int
    word_count: int