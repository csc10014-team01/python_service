"""Lab 4 Part C: warm-up exercises P1-P5.

Run from this folder: uvicorn hello_api:app --reload
Then open http://127.0.0.1:8000/docs in your browser.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Hello API")


# P1: the simplest endpoint.
@app.get("/")
def home() -> dict:
    return {"message": "Hello, CSC10014!"}


# P2: read a name from the path.
@app.get("/hello/{name}")
def hello(name: str) -> dict:
    return {"message": f"Hello, {name}!"}


# P3: read an integer from the query string.
@app.get("/square")
def square(n: int) -> dict:
    return {"n": n, "square": n * n}


# P4: validate two numbers in the JSON request body.
class Numbers(BaseModel):
    a: float
    b: float


@app.post("/add")
def add(nums: Numbers) -> dict:
    return {"sum": nums.a + nums.b}


# P5: return 404 when the requested course does not exist.
COURSES = {"CSC10014": "Computational Thinking", "CSC10001": "Fundamentals of Programming"}


@app.get("/courses/{code}")
def course(code: str) -> dict:
    if code not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"code": code, "name": COURSES[code]}
