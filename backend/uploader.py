import os
import argparse
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import pandas as pd
import time
from config import (
    QDRANT_API_KEY, 
    QDRANT_URL, 
    ENCODING_MODEL,
    COLLECTION_NAME,
    DATA_FILE_NAME,
)

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", help=f"Source file for data. Usually saved as {DATA_FILE_NAME}", default=os.path.join(os.getcwd(), DATA_FILE_NAME))
parser.add_argument("-k", "--skip", help="Skip k batches", required=False)

args = parser.parse_args()

model = SentenceTransformer(ENCODING_MODEL)
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY,)

def encodeAndUpload(path, skip):
    print("Getting preloaded data...")
    df = pd.read_csv(args.source)

    maxIndex = client.get_collection(collection_name=COLLECTION_NAME).points_count
    
    print(('*' * 25) + "\nStart transfer")

    # Create data batches for the text extracted and encode them using the SentenceTransformer Model.
    batch_size = 512
    batch = []
    ctr = 0
    transfer_start = time.time()
    for id, currentRow in df.iterrows():
        batch.append(currentRow["content"])
        if len(batch) >= batch_size:
            if ctr > skip:
                batch_start = time.time()
                error = False
                print(f"Encoding batch {ctr}", end="")
                try:
                    upBatch = (model.encode(batch))
                except Exception as e:
                    print(f" -- *Error with encoding* -- {type(e).__name__}")
                    error = True
                if not error:
                    try:
                        client.upsert(
                            collection_name=COLLECTION_NAME,
                            points=models.Batch(
                                ids=[i for i in range(maxIndex + (ctr*batch_size), maxIndex + (ctr*batch_size) + id + 1)],
                                payloads=[
                                    {
                                        "text": row["content"],
                                        "title": row["document"]
                                    }
                                    for _, row in df[ctr*batch_size:id+1].iterrows()
                                ],
                                vectors=[v.tolist() for v in upBatch]
                            ),
                        )
                        print(f" -- completed in {time.time()-batch_start} seconds")
                    except Exception as e:
                        print(f" -- *Error with upload* -- {type(e).__name__}")
            else:
                print(f"Skipped batch {ctr}")
            batch = []
            ctr+=1

    if len(batch) > 0:
        batch_start = time.time()
        print(f"Encoding batch {ctr} (last)", end="")
        upBatch = (model.encode(batch))
        client.upsert(
                collection_name=COLLECTION_NAME,
                points=models.Batch(
                    ids=[i for i in range(maxIndex + (ctr*batch_size), (maxIndex + (ctr*batch_size)) + len(upBatch))],
                    payloads=[
                        {
                            "text": row["content"],
                            "title": row["document"]
                        }
                        for _, row in df[ctr*batch_size:].iterrows()
                    ],
                    vectors=[v.tolist() for v in upBatch]
                ),
            )
        batch = []
        print(f" -- completed in {time.time()-batch_start} seconds")
    print(f"Finish transfer -- completed in {time.time()-transfer_start} seconds\n{('*' * 25)}")

if __name__ == "__main__":
    if os.path.isfile(args.source) and args.source.endswith(".csv"):
        number = -1
        if args.skip:
            number = int(args.skip)
        encodeAndUpload(args.source, number)
    else:
        print("Specified file was not found.\nExiting...")