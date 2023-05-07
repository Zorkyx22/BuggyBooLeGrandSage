import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

QDRANT_API_KEY=os.getenv('QDRANT_API_KEY')
QDRANT_URL=os.getenv('QDRANT_URL')

ENCODING_MODEL=os.getenv('ENCODING_MODEL')
DATA_FILE_NAME=os.getenv('DATA_FILE_NAME')
COLLECTION_NAME=os.getenv('COLLECTION_NAME')