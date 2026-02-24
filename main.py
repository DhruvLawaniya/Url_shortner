import os
import string
import random
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- 1. DATABASE CONFIGURATION ---
# This handles both your local laptop (SQLite) and Render (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Fix for SQLAlchemy/PostgreSQL compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fix for SSL requirement on cloud databases like Neon/Supabase
if "postgresql" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. DATABASE MODEL ---
class URLModel(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String, index=True)
    short_code = Column(String, unique=True, index=True)
    clicks = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

# --- 3. FASTAPI SETUP ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Helper to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# --- 4. ROUTES ---

# HOME PAGE: Shows the form and the analytics table
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, short_url: str = None, db: Session = Depends(get_db)):
    # Fetch all links from database for the analytics table
    history = db.query(URLModel).order_by(URLModel.id.desc()).all()
    
    # If a short_url was passed in the query string (after shortening), format it
    full_short_link = None
    if short_url:
        full_short_link = f"{request.base_url}{short_url}"
        
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "history": history, 
        "short_url": full_short_link
    })

# SHORTEN LOGIC: Handles form submission
@app.post("/shorten")
async def shorten_url(url: str = Form(...), db: Session = Depends(get_db)):
    # Clean the URL (remove trailing slashes to avoid near-duplicates)
    url = url.strip().rstrip("/")

    # STEP 1: Check if this long URL already exists (Deduplication)
    existing_entry = db.query(URLModel).filter(URLModel.long_url == url).first()
    
    if existing_entry:
        code = existing_entry.short_code
    else:
        # STEP 2: Create new short code if it's a new URL
        code = generate_short_code()
        new_entry = URLModel(long_url=url, short_code=code)
        db.add(new_entry)
        db.commit()

    # STEP 3: REDIRECT back to home with the code in the URL
    # This is the "PRG Pattern" that prevents the "Reload" bug
    return RedirectResponse(url=f"/?short_url={code}", status_code=303)

# REDIRECT LOGIC: Handles clicking a short link
@app.get("/{code}")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URLModel).filter(URLModel.short_code == code).first()
    
    if url_entry:
        # STEP 4: Update Click Analytics
        url_entry.clicks += 1
        db.commit()
        return RedirectResponse(url=url_entry.long_url)
    
    raise HTTPException(status_code=404, detail="URL not found")

# --- 5. RUNNER (For Local Testing) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)