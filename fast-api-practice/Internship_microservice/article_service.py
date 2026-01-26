from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

app=FastAPI()

# In-memory stores for demo use; Should be replaced with durable storage in production.
ARTICLES_DB = {}
CONFIRMED_LABELS_DB = {}
SUGGESTION_DB={}

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
    
class CategoryConfirmIn(BaseModel):
    category: str
    location: Optional[str] = None
    accepted : bool
    
def get_article_or_404(article_id: str) -> ArticleOut:
    # Centralized fetch that raises a 404 when the article is missing.
    article = ARTICLES_DB.get(article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/")
def root():
    # Simple liveness message.
    return{"message": "Hello from Article Service"}    

@app.get("/health")
def health_check():
    # Health probe; extend with dependency checks if needed.
    return{"status": "Article Service is healthy"}

@app.get("/articles/{article_id}", response_model = ArticleOut)
def get_article(article_id: str):
    return get_article_or_404(article_id)
    
    
@app.get("/articles/{article_id}/category")
def get_confirmed_category(article_id : str):
    get_article_or_404(article_id)
    
    decision = CONFIRMED_LABELS_DB.get(article_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="No confirmed category for this article")   
    
    return{
        "article_id": article_id,
        "category": decision.category,
        "location": decision.location,
        "accepted": decision.accepted
    }
    
@app.get("/articles/{article_id}/status")
def get_article_status(article_id : str):
    get_article_or_404(article_id)
    
    status = {
        "article_id": article_id,
        "has_suggestion": article_id in SUGGESTION_DB,
        "category_confirmed": article_id in CONFIRMED_LABELS_DB
    }
    return status

@app.get("/articles/{article_id}/audit")
def audit_article(article_id: str):
    # Returns both the suggested classification and any user confirmation for auditing/debug.
    get_article_or_404(article_id)

    suggestion = SUGGESTION_DB.get(article_id)
    decision = CONFIRMED_LABELS_DB.get(article_id)

    return {
        "article_id": article_id,
        "suggestion": suggestion,
        "decision": decision
    }


 
             
    
@app.post("/articles", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(article: ArticleIn):
    
    article_id = str(uuid4())
    
    created = ArticleOut(id=article_id, **article.model_dump())
    
    ARTICLES_DB[article_id] = created
    
    return created

@app.post("/articles/{article_id}/classify", response_model = ClassificationOut)
def classify_article(article_id : str):
    
    article = get_article_or_404(article_id)    
    
    # Mock classification logic until an NLP model is integrated.
    
    suggestion = ClassificationOut(
        article_id = article_id,
        category = "local news",
        location = None,
        confidence = 0.20,
        notes = "Mock classification - no model integrated yet  "
    )
    SUGGESTION_DB[article_id] = suggestion
    return suggestion
    
    
@app.post("/articles/{article_id}/confirm-category")
def confirm_category(article_id: str,decision: CategoryConfirmIn):
    
    article = get_article_or_404(article_id)    
    # Persist the user feedback so it can be revisited or used for training.
    CONFIRMED_LABELS_DB[article_id]= decision
    
    return{"article_id":article_id, "saved":True}