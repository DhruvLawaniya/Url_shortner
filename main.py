import string
import random
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Database Setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class URLModel(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String)
    short_code = Column(String, unique=True)
    clicks = Column(Integer, default=0)  # <-- NEW: Analytics column

Base.metadata.create_all(bind=engine)

# 2. FastAPI Setup
app = FastAPI()
templates = Jinja2Templates(directory="templates")

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# 3. Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    db = SessionLocal()
    # Fetch all links from newest to oldest to show in a table
    history = db.query(URLModel).order_by(URLModel.id.desc()).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "history": history})

@app.post("/shorten", response_class=HTMLResponse)
async def shorten_url(request: Request, url: str = Form(...)):
    db = SessionLocal()
    code = generate_short_code()
    new_entry = URLModel(long_url=url, short_code=code)
    db.add(new_entry)
    db.commit()
    
    # Refresh history to show the new link immediately
    history = db.query(URLModel).order_by(URLModel.id.desc()).all()
    short_link = f"{request.base_url}{code}"
    db.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "short_url": short_link,
        "history": history
    })

@app.get("/{code}")
def redirect_to_url(code: str):
    db = SessionLocal()
    url_entry = db.query(URLModel).filter(URLModel.short_code == code).first()
    
    if url_entry:
        # Update Analytics: Increment the click count
        url_entry.clicks += 1
        db.commit()
        long_url = url_entry.long_url
        db.close()
        return RedirectResponse(url=long_url)
    
    db.close()
    raise HTTPException(status_code=404, detail="URL not found")