import psycopg2
from typing import List   
import os
from qdrant_client import QdrantClient, models

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
VECTOR_DISTANCE = os.getenv("VECTOR_DISTANCE")
VECTOR_SIZE = 6 # always 6, because we have 6 emotion scores (joy, anger, fear, love, sadness, surprise)

def connect_to_db():
    # Connect to PostgreSQL database
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="postgres",
            user="postgres",
            password="postgres",
        )
        print("Connected to the database successfully!")
        
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        exit()
        
    # Create a cursor object to interact with the database
    return conn.cursor()

def get_actor_embeddings(cursor) -> List[list]:
    # Get all actor embeddings from the database for the different actors
    # for this join the table "ActorClassifier" and "Actor" on the column "actorId"
    cursor.execute('''
        SELECT "Actor"."name", 
            "ActorClassifier"."joyScore",
            "ActorClassifier"."angerScore",
            "ActorClassifier"."fearScore",
            "ActorClassifier"."loveScore",
            "ActorClassifier"."sadnessScore",
            "ActorClassifier"."surpriseScore",
            "Actor"."headshotUrl"
        FROM public."ActorClassifier"
        INNER JOIN public."Actor"
        ON "Actor"."id" = "ActorClassifier"."actorId";
    ''')
    
    actors = cursor.fetchall()
    print(f"Number of actors: {len(actors)}")
    return actors

def check_collection_exists(qdrant_client: QdrantClient) -> bool:
    # Check if a collection exists in Qdrant
    try:
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
        if collection_info:
            print(f"Collection {QDRANT_COLLECTION_NAME} already exists.")
            return True
        else:
            print(f"Collection {QDRANT_COLLECTION_NAME} does not exist.")
            return False
    except Exception as e:
        print(f"Error checking collection existence: {e}")
        return False


def create_collection(qdrant_client: QdrantClient) -> bool:
    # Create a new collection in Qdrant
    try:
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(size=6, distance=VECTOR_DISTANCE),
        )
        
        print(f"Collection {QDRANT_COLLECTION_NAME} created successfully.")
        return True
    except Exception as e:
        print(f"Error creating collection: {e}")
        return False
    


def upload_embeddings_to_qdrant(qdrant_client: QdrantClient, embeddings: List[list]):
    # structure of the embeddings:
    # [(actorName, joyScore, angerScore, fearScore, loveScore, sadnessScore, surpriseScore, headshotUrl), (...), ...]
    
    try:
        # first we need to create the point structs for the embeddings
        points = []
        for i in range(len(embeddings)):
            point = models.PointStruct(
                id=i+1,  # we start with 1
                payload={
                    "name": embeddings[i][0],  # actorName
                    "headshotUrl": embeddings[i][7],  # headshotUrl
                },
                vector=[
                    embeddings[i][1],  # joyScore
                    embeddings[i][2],  # angerScore
                    embeddings[i][3],  # fearScore
                    embeddings[i][4],  # loveScore
                    embeddings[i][5],  # sadnessScore
                    embeddings[i][6]   # surpriseScore
                ],
            )
            points.append(point)
            
        # now we just upload the points to Qdrant
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )
        print(f"Uploaded {len(points)} embeddings to Qdrant.")
        
    except Exception as e:
        print(f"Error uploading embeddings: {e}")
        
    
            
if __name__ == "__main__":
    
    # connect to the PostgreSQL database
    postgres_cursor = connect_to_db() 

    # get qdrant client
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, prefer_grpc=False, port=443, check_compatibility=False)
    
    # if the collection already exists, exit the script
    if check_collection_exists(qdrant_client):
        exit()    
    
    # if here -> the collection does not exist, get the embeddings from the database 
    actor_embeddings = get_actor_embeddings(postgres_cursor)
    postgres_cursor.close()
    
    # create the collection in Qdrant and if successful, upload the embeddings to Qdrant
    if create_collection(qdrant_client):
       upload_embeddings_to_qdrant(qdrant_client=qdrant_client, embeddings=actor_embeddings) 
    