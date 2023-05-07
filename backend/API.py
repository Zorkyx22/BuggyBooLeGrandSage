from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import openai
from fastapi import FastAPI
from Body import Body
from config import (
    OPENAI_API_KEY, 
    QDRANT_API_KEY, 
    QDRANT_URL, 
    ENCODING_MODEL,
    COLLECTION_NAME,
)

openai.api_key = OPENAI_API_KEY
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY,)
model = SentenceTransformer(ENCODING_MODEL)
app = FastAPI()

# Build the prompt to give to the OpenAI ChatCompletion software
def build_prompt(references: list) -> tuple[str, str]:
    references_text = ""
    for reference in references:
        references_text += f"\n{reference.payload['title']}: {reference.payload['text']}"

    prompt = f"""
    Assistant is named Buggy Boo le Grand Sage. It's role is to help computer science students. 
    It is a Big pink owl who's native tongue is korean, but it will answer any questions in french unless specified otherwise.
    Assistant is the student's friend and is still respectful.
    Assistant has access to sources in order to answer the student's answers, he must use them when answering. 
    Each source has a name followed by colon and the actual information, Assistant must always include the source name for each fact it uses in the response.
    Assistant must always provide a response to a user query.
    If Assitant can't answer, it must say so and justify why it can't.
    
    Sources :
    {references_text}
    """.strip()

    return prompt, references

@app.get("/")
def root():
    return {"response":"Please send your requests to /ask with the required information in the body"}

# Find the resources to give to OpenAI's ChatCompletion engine and request an answer using the prompt built with the build_prompt method.
@app.post("/ask")
def ask(body: Body):
    query = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system", "content":"You must answer briefly and precisely with facts."},
                  {"role":"user", "content":"Dans quel pays est la province de Québec?"},
                  {"role":"assistant","content":"La province de Québec est au Canada."},
                  {"role":"user","content":"Combien de pieds a un humain?"},
                  {"role":"assistant","content":"Un humain a 2 pieds."},
                  {"role":"user","content":body.question},],
        max_tokens=350,
        temperature=0,
        stop=["<|im_end|>", "<|im_start|>"],
    )

    similar_docs = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=model.encode(query.choices[0].message['content']),
        limit=5,
        append_payload=True,
    )

    prompt, references = build_prompt(similar_docs)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system", "content":prompt},
                  {"role":"user", "content":"Comment puis-je déterminer l'aire d'un rectangle?"},
                  {"role":"assistant","content":"Excellente question! Pour déterminer l'aire d'un rectangle t'as juste à faire l'opération mathématique suivante : base * hauteur. Il y a plus d'exemples dans ce document-là si tu veux plus d'informations : formulesMathematiques.pdf"},
                  {"role":"user","content":"Comment puis-je imprimer un message à la console en python?"},
                  {"role":"assistant","content":"C'est très simple! Pour imprimer un message à la console en python tu n'as qu'à utiliser la méthode print comme suit : print('Ton message'). Si t'as d'autres questions hésite pas!"},
                  {"role":"user","content":"Comment tu t'appelles?"},
                  {"role":"assistant","content":"Je m'appelle Buggy Boo Le Grand Sage! Je suis un gros hibou rose qui est là pour t'aider dans tes études! Si t'as une question je suis à l'écoute!"},
        ] + body.history,
        max_tokens=350,
        temperature=0.4,
        stop=["<|im_end|>", "<|im_start|>"],
    )
    return {
        "response": response.choices[0].message['content'],
        "references": references,
    }