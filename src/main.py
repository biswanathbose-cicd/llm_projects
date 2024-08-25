
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from langchain_helper import get_qa_chain
import uvicorn
import os

app = FastAPI()

# Define a model for the response
class QAResponse(BaseModel):
    result: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <html>
        <head>
            <title>Bistalks Q&A 🌱</title>
        </head>
        <body>
            <h1>Bistalks Q&A 🌱</h1>
            <form action="/ask-question" method="post">
                <label for="question">Question:</label><br>
                <input type="text" id="question" name="question"><br><br>
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# @app.post("/ask-question", response_model=QAResponse)
# async def ask_question(question: str = Form(...)):
#     # chain = get_qa_chain()
    
#     # response = chain(question)
#     response = get_qa_chain(question)
#     print(f"Type of chain: {type(get_qa_chain(question))}")
#     print(f"Response: {response}")
#     return QAResponse(result=response)
@app.post("/ask-question", response_model=QAResponse)
async def ask_question(question: str = Form(...)):
    chain = get_qa_chain()
    response = chain(question)

    # Assuming `response` is an object, and you need to extract the answer
    # For example, if the result is in response["result"]:
    result_text = response["result"] if isinstance(response, dict) and "result" in response else str(response)

    return QAResponse(result=result_text)


# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# def root():
#     return {"Hello": "World"}
