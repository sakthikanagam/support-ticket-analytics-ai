from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from data_loader import load_data
from llm_service import get_intent
from query_engine import execute_query
from anomaly_detector import detect_anomalies

app = FastAPI(
    title="Support Ticket Analytics",
    version="1.0"
)

# -------------------------------------
# Static Files
# -------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# -------------------------------------
# Templates
# -------------------------------------

templates = Jinja2Templates(
    directory="templates"
)

# -------------------------------------
# Load Dataset Once
# -------------------------------------

df = load_data()

# -------------------------------------
# Request Model
# -------------------------------------

class QueryRequest(BaseModel):
    question: str

# -------------------------------------
# Home Page
# -------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )

# -------------------------------------
# Health Check
# -------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "rows_loaded": len(df)
    }

# -------------------------------------
# Anomaly Detection
# -------------------------------------

@app.get("/anomalies")
def anomalies():

    try:

        result = detect_anomalies(df)

        return result

    except Exception as e:

        return {
            "error": str(e)
        }

# -------------------------------------
# Natural Language Query
# -------------------------------------

@app.post("/query")
def query(payload: QueryRequest):

    try:

        question = payload.question.strip()

        print("=" * 50)
        print("QUESTION:", question)

        plan = get_intent(question)

        print("PLAN:", plan)

        answer = execute_query(
            df,
            plan
        )

        return jsonable_encoder({
            "question": question,
            "plan": plan,
            "answer": answer
        })

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "error": str(e)
        }

# -------------------------------------
# Startup Message
# -------------------------------------

@app.on_event("startup")
def startup():

    print("=" * 60)
    print("Support Ticket Analytics Started")
    print(f"Rows Loaded : {len(df)}")
    print("=" * 60)