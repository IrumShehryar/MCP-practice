from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

app=FastAPI()

ARTICLES_DB = {}

class ArticleIn(BaseModel):
    title: str
    text: str
    url: Optional[str]= None
    source: Optional[str]= None
    lang: Optional[str]= None
    
class ArticleOut(ArticleIn):
    id: str
    
class ClassificationOut(BaseModel):
    article_id : str
    category: str
    location : Optional[str] = None
    confidence : float
    notes : Optional[str] = None

@app.get("/")
def root():
    return{"message": "Hello from Article Service"}    

@app.get("/health")
def health_check():
    return{"status": "Article Service is healthy"}

@app.get("/articles/{article_id}", response_model = ArticleOut)
def get_article(article_id: str):
    article = ARTICLES_DB.get(article_id)
    if article is None:
        return HTTPException(status_code = 404,detail = "Article not found")
    return article
    
    
@app.post("/articles", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(article: ArticleIn):
    
    article_id = str(uuid4())
    
    created = ArticleOut(id=article_id, **article.model_dump())
    
    ARTICLES_DB[article_id] = created
    
    return created

@app.post("/articles/{article_id}/classify", response_model = ClassificationOut)
def classify_article(article_id : str):
    
    article = ARTICLES_DB.get(article_id)
    if article is None:
        raise HTTPException(status_code = 404,detail = "Article not found")    
    
    
    #mock classification logic no NLP model integrated yet
    
    return ClassificationOut(
        article_id = article_id,
        category = "local news",
        location = None,
        confidence = 0.20,
        notes = "Mock classification - no model integrated yet  "
    )