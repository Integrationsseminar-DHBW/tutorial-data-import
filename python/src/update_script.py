import requests
from python.src.upload_to_qdrant import connect_to_db
import time
from dotenv import load_dotenv
import os

def get_actor_data(postgres_cursor):
    # get all actors from the database
    postgres_cursor.execute('''
        SELECT "Actor"."id",
            "Actor"."name", 
            "Actor"."updated_headshot"
        FROM public."ActorClassifier"
        INNER JOIN public."Actor"
        ON "Actor"."id" = "ActorClassifier"."actorId"
        WHERE "updated_headshot" = 'False' or "updated_headshot" IS NULL
    ''')
    actors = postgres_cursor.fetchall()
    
    print(f"Number of actors: {len(actors)}")
    
    # create a list of actor data
    actor_data = []
    for actor in actors:
        actor_data.append({
            "id": actor[0],
            "name": actor[1],
            "updated_headshot": actor[2]
        })
    
    return actor_data

def get_actor_image(name):
    # load environment variables from .env file
    load_dotenv()
    # get the api key from the environment variables
    api_key = os.getenv("THE_MOVIE_DB_API_KEY")
    
    # get the actor image from the tmdb api
    url = f"https://api.themoviedb.org/3/search/person?query={name}"
    headers = {
        "accept": "application/json",
        "Authorization": f'Bearer {api_key}' 
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200 or response.json()["total_results"] == 0:
        print(f"Error: {response.status_code}, with actor {name}")
        return None
    
    # get the profile path from the response
    profile_path = response.json()["results"][0]["profile_path"]
    # check if the profile path is None
    if profile_path is None:
        print(f"No profile path found for actor {name}") 
        return None
    
    # create the new headshot url
    new_headshot_url = f"https://image.tmdb.org/t/p/w500{profile_path}"
    print(f"New headshot url: {new_headshot_url} for actor {name}")
    return new_headshot_url

def update_headshoturl(postgres_cursor, actor, image_link):
    if image_link is not None:
        postgres_cursor.execute('''
            UPDATE "Actor"
            SET "updated_headshot" = 'True',
            "headshotUrl" = %s
            WHERE "id" = %s
        ''', (image_link, actor["id"]))
        
        # commit the changes to the database
        postgres_cursor.connection.commit()
        
        print(f"Updated headshot url for actor {actor['name']} to {image_link}, id: {actor['id']}")
       

if __name__ == "__main__":
    # connect to the PostgreSQL database
    postgres_cursor = connect_to_db() 

    # call the function to get all actors
    actors = get_actor_data(postgres_cursor)

    # get the new headshot urls from the tmdb api for the first 10 actors
    for actor in actors:
        # get the actor image from the tmdb api
        image_link = get_actor_image(actor["name"])
        print(f"Actor: {actor['name']}, got image link: {image_link}")
        
        # update the headshot urls in the database, if a new one is found
        update_headshoturl(postgres_cursor, actor, image_link)
        
        # only do 20 updates per second, to not overload the tmdb api
        time.sleep(0.05)
    
    # close the cursor and connection to the database
    postgres_cursor.close()