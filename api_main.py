from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from agent import process_customer_query
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="E-Commerce Query Analyzer API")


# Input model
class QueryRequest(BaseModel):
    query: str


@app.post("/analyze")
async def analyze_query(payload: QueryRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Empty query provided.")

    result = await process_customer_query(query)

    if not result["success"]:
        raise HTTPException(status_code=422, detail=result["error"])

    return {"metadata": result["data"]}
