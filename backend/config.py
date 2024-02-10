import os
from dotenv import load_dotenv
from qdrant_client.http import models

load_dotenv()

OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
QDRANT_API_KEY=os.getenv('QDRANT_API_KEY')

QDRANT_PROTOCOL='http'
QDRANT_PORT=6333
QDRANT_URL=f"{QDRANT_PROTOCOL}://localhost"

QDRANT_BATCH_SIZE = 512

ENCODING_MODEL='multi-qa-MiniLM-L6-cos-v1'
ENCODING_MODEL_SIZE=384
ENCODING_MODEL_FUNCTION=models.Distance.DOT
ENCODING_MODEL_FUNCTION="Dot"

DATA_FILE_NAME='data.csv'
COLLECTION_NAME='DocumentsScolaires'

BACKEND_PROTOCOL = 'http'
BACKEND_PORT = 8000
BACKEND_URL = f"{BACKEND_PROTOCOL}://127.0.0.1:{BACKEND_PORT}"