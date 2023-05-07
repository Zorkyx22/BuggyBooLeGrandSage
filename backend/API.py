import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import openai
from fastapi import FastAPI, Request
from pydantic import BaseModel
from config import (
    OPENAI_API_KEY, 
    QDRANT_API_KEY, 
    QDRANT_URL, 
    ENCODING_MODEL,
    COLLECTION_NAME,
    DATA_FILE_NAME,
)

openai.api_key = OPENAI_API_KEY
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY,)
model = SentenceTransformer(ENCODING_MODEL)
app = FastAPI()

turn_prefix = """
<|im_start|>user
"""

turn_suffix = """
<|im_end|>
<|im_start|>assistant
"""

class Body(BaseModel):
    history: str

# Build the prompt to give to the OpenAI ChatCompletion software
def build_prompt(question: str, references: list, prompt_history: str) -> tuple[str, str]:
    references_text = ""
    for reference in references:
        references_text += f"\n{reference.payload['title']}: {reference.payload['text']}"

    prompt = f"""<|im_start|>system
    Assistant is named Buggy Boo le Grand Sage. It's role is to help computer science students. 
    Assistant is the student's friend and is still respectful.
    Assistant has access to sources in order to answer the student's answers, he must use them when answering. 
    Each source has a name followed by colon and the actual information, Assistant must always include the source name for each fact it uses in the response.
    Assistant must always provide a response to a user query.
    If Assitant can't answer, it must say so and justify why it can't.
    
    Sources :
    {references_text}
    <|im_end|>

    {prompt_history}
    {question}{turn_suffix}
    """.strip()

    return prompt, references

# Find the resources to give to OpenAI's ChatCompletion engine and request an answer using the prompt built with the build_prompt method.
@app.post("/ask/{question}")
async def ask(question: str, body: Body):

    query = openai.Completion.create(
        engine="TestGPT35Turbo",
        prompt=question,
        max_tokens=350,
        temperature=0.2,
        stop=["<|im_end|>", "<|im_start|>"],
    )

    similar_docs = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=model.encode(query),
        limit=5,
        append_payload=True,
    )

    prompt, references = build_prompt(question, similar_docs, body.history)

    response = openai.Completion.create(
        engine="TestGPT35Turbo",
        prompt=prompt,
        max_tokens=350,
        temperature=0.2,
        stop=["<|im_end|>", "<|im_start|>"],
    )
    return {
        "response": response.choices[0].text,
        "references": references,
    }