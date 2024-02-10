import requests
import os
import argparse
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

import multiprocessing as mp
from multiprocessing import Process, Lock
from concurrent.futures import ThreadPoolExecutor

from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

os.environ["TOKENIZERS_PARALLELISM"] = "true"

progress = Progress(
    TextColumn("[bold green]{task.fields[task_name]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    SpinnerColumn("dots"),
    TimeRemainingColumn(),
)


import pandas as pd
import time
from config import (
    QDRANT_API_KEY, 
    QDRANT_URL,
    QDRANT_PORT,
    QDRANT_BATCH_SIZE,
    ENCODING_MODEL,
    ENCODING_MODEL_SIZE,
    ENCODING_MODEL_FUNCTION,
    COLLECTION_NAME,
    DATA_FILE_NAME,
)

parser = argparse.ArgumentParser()
parser.add_argument("source", help=f"Source CSV file to be uploaded")
parser.add_argument("-s", "--skip", help=f"Skip k batches (batches are {QDRANT_BATCH_SIZE} chunks long)")

args = parser.parse_args()

model = SentenceTransformer(ENCODING_MODEL)
client = QdrantClient(QDRANT_URL, port=QDRANT_PORT)

def LoadIntoDataframe(path):
    chunks = []
    counter = 0
    total_lines = sum(1 for row in open(path))
    task_name_template = "Loading Data Chunk"
    load_task_id = progress.add_task("load", task_name=task_name_template, start=True, total=total_lines)
    for chunk in pd.read_csv(path, chunksize=1, on_bad_lines='warn'):
        counter+=1
        chunks.append(chunk)
        progress.update(load_task_id, task_name=task_name_template+f" {counter}", advance=1)
    df = pd.concat(chunks, axis=0)
    progress.update(load_task_id, task_name=task_name_template+f" - COMPLETED", advance=(total_lines-counter))
    return df

def EncodeBatches(df, skip, lock):
    ctr = 0
    batch = []
    all_batches = []
    maxIndex = client.get_collection(collection_name=COLLECTION_NAME).points_count

    encode_task_name_template = "Encoding batch"
    upload_task_name_template = "Uploading batch"

    batch_count = int(df.shape[0]/QDRANT_BATCH_SIZE)
    if skip > 0:
        batch_count+=1

    encode_task_id = progress.add_task("encode", task_name=encode_task_name_template, start=True, total=batch_count+1)
    upload_task_id = progress.add_task("encode", task_name=upload_task_name_template, start=True, total=batch_count+1)

    with ThreadPoolExecutor(max_workers=1) as executor:
        for id, currentRow in df.iterrows():
            if (type(currentRow['content'])==str):
                batch.append(currentRow['content'])

                if len(batch) >= QDRANT_BATCH_SIZE:
                    progress.update(encode_task_id, task_name=encode_task_name_template+f" {ctr}", advance=1)
                    
                    if ctr > skip:
                        batch_start = time.time()
                        error = False
                        try:
                            upBatch = (model.encode(batch))
                        except Exception as e:
                            print(f"-=[ Batch {ctr} : Error with encoding -- {type(e).__name__} ]=-")
                            error = True
                        
                        if not error:
                            executor.submit(UploadBatchAsync, ctr, len(batch), upBatch, maxIndex, upload_task_id, upload_task_name_template, lock)
                    batch = []
                    ctr+=1

        if len(batch) > 0:
            progress.update(encode_task_id, task_name=encode_task_name_template+f" {ctr}", advance=1)
            try:
                upBatch = (model.encode(batch))
            except Exception as e:
                print(f"-=[ Batch {ctr} : Error with encoding -- {type(e).__name__} ]=-")
                error = True
            executor.submit(UploadBatchAsync, ctr, len(batch), upBatch, maxIndex, upload_task_id, upload_task_name_template, lock, True)
            batch = []

        executor.shutdown(wait=True)
        progress.update(encode_task_id, task_name=encode_task_name_template+f" - COMPLETED", advance=1)

def UploadBatchAsync(id, size, encoded_batch, maxIndex, upload_task_id, task_name_template, lock, last_batch=False):
    lock.acquire()
    try:
        progress.update(upload_task_id, task_name=task_name_template+f" {id}", advance=1)
        start_position = id*QDRANT_BATCH_SIZE
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=models.Batch(
                ids=[i for i in range(maxIndex + (id*QDRANT_BATCH_SIZE), maxIndex + (id*QDRANT_BATCH_SIZE) + size)],
                payloads=[
                    {
                        "text": row["content"],
                        "title": row["document"],
                    }
                    for _, row in df[start_position:start_position+size].iterrows()
                ],
                vectors=[v.tolist() for v in encoded_batch]
            ),
        )
    except Exception as e:
        print(f"-=[ Batch {id} : Error with upload -- {type(e).__name__} -- {e.message}")
    finally:
        lock.release()
        if last_batch:
            progress.update(upload_task_id, task_name=task_name_template+f" - COMPLETED", advance=1)

if __name__ == "__main__":
    if os.path.isfile(args.source) and args.source.endswith(".csv"):
        number = -1
        if args.skip:
            number = int(args.skip)
        with progress:
            lock = Lock()
            df = LoadIntoDataframe(args.source)
            EncodeBatches(df, number, lock)
    else:
        print("Specified file was not found.\nExiting...")