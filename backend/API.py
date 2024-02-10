from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import openai
import tiktoken
from Body import Body

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from config import (
    OPENAI_API_KEY, 
    QDRANT_API_KEY, 
    QDRANT_URL, 
    QDRANT_PORT,
    ENCODING_MODEL,
    COLLECTION_NAME,
)
from prompts import QUERY_PROMPT, BUGGY_PROMPT, BUGGY_INFORMATION_PROMPT

app = FastAPI()
openai.api_key = OPENAI_API_KEY
client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY,)
model = SentenceTransformer(ENCODING_MODEL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def BuildReferences(references: list) -> str:
    references_text = ""
    for reference in references:
        references_text += f"\n{reference.payload['title']}: {reference.payload['text']}"
    return references_text.strip()


def LastPage(history: list):
    counter = 6000
    returnedList = []
    history.reverse()
    for item in history:
        counter -= len(item['content'])
        if counter >= 0:
            returnedList.append(item)
        else:
            break
    return returnedList

def GenerateQuery(history: list[dict[str, str]]) ->str:
    return openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=LastPage(history) + [{"role":"system", "content":QUERY_PROMPT}],
        max_tokens=350,
        temperature=0
    ).choices[0].message.content

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


def StreamGenerator(body: Body):
    openai_stream = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system", "content":BUGGY_PROMPT}] + LastPage(body.conversation) + [{"role":"system", "content":FindSources(body.conversation)}],
        max_tokens=1000,
        temperature=0.5,
        stream=True
    )
    for event in openai_stream:
        if "content" in event["choices"][0].delta:
            current_response = event["choices"][0].delta.content
            yield "data: " + current_response + "\n\n"


@app.post("/ask")
def ask(body: Body):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system", "content":BUGGY_PROMPT}] + LastPage(body.conversation) + [{"role":"system", "content":FindSources(body.conversation)}],
        max_tokens=1000,
        temperature=0.7
    )
    return {
        "response": response.choices[0].message.content
    }

@app.post("/ask_streaming")
def ask(body: Body):
    return StreamingResponse(StreamGenerator(body), media_type='text/event-stream')

@app.post("/chat")
def chat(body: Body):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[{"role":"system","content":"Traitez votre interlocuteur comme un bon ami. Répondez toujours en moins de 1000 mots."}] + LastPage(body.conversation)
    )
    return {
        "response": response.choices[0].message.content
    }