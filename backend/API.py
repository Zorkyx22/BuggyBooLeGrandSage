from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import openai
import tiktoken
from Body import Body
from fastapi import FastAPI
from config import (
    OPENAI_API_KEY, 
    QDRANT_API_KEY, 
    QDRANT_URL, 
    ENCODING_MODEL,
    COLLECTION_NAME,
)
from prompts import QUERY_PROMPT, BUGGY_PROMPT, BUGGY_INFORMATION_PROMPT

openai.api_key = OPENAI_API_KEY
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY,)
model = SentenceTransformer(ENCODING_MODEL)
app = FastAPI()

def BuildReferences(references: list) -> str:
    references_text = ""
    for reference in references:
        references_text += f"\n{reference.payload['title']}: {reference.payload['text']}"
    return references_text.strip()


def LastPage(history: list):
    counter = 6000
    returnedList = []
    for item in history.reverse():
        counter -= len(item['content'])
        if counter >= 0:
            returnedList.append(item)
        else:
            break
    return returnedList

def GenerateQuery(history: list[dict[str, str]]) ->str:
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=LastPage(history) + [{"role":"system", "content":QUERY_PROMPT}],
        max_tokens=350,
        temperature=0
    ).choices[0].message['content']

def FindSources(history: list) -> str:
    query = GenerateQuery(history)
    sources = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=model.encode(query),
        limit=5,
        score_threshold=0.4,
        append_payload=True,
    )
    return BUGGY_INFORMATION_PROMPT.format(BuildReferences(sources))

# Find the resources to give to OpenAI's ChatCompletion engine and request an answer using the prompt built with the build_prompt method.
@app.post("/ask")
def ask(body: Body):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system", "content":BUGGY_PROMPT}] + LastPage(body.conversation) + [{"role":"system", "content":FindSources(body.conversation)}],
        max_tokens=1000,
        temperature=0.7
    )
    return {
        "response": response.choices[0].message['content']
    }