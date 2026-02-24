import string
import random
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# 1. Database Setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Database Model
class URLModel(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String)
    short_code = Column(String, unique=True)

Base.metadata.create_all(bind=engine)

# 3. FastAPI App
app = FastAPI()

# Pydantic schema for the request
class URLCreate(BaseModel):
    url: str

# Helper to generate a random code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.post("/shorten")
def shorten_url(item: URLCreate):
    db = SessionLocal()
    code = generate_short_code()
    
    # Save to database
    new_entry = URLModel(long_url=item.url, short_code=code)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    db.close()
    
    return {"short_url": f"http://localhost:8000/{code}"}

@app.get("/{code}")
def redirect_to_url(code: str):
    db = SessionLocal()
    url_entry = db.query(URLModel).filter(URLModel.short_code == code).first()
    db.close()
    
    if url_entry:
        return RedirectResponse(url=url_entry.long_url)
    raise HTTPException(status_code=404, detail="URL not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)