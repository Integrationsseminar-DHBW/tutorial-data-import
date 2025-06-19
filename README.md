# tutorial-data-import

This project sets up a workflow to import actor embedding vectors from a PostgreSQL `.sql` file into a Qdrant database. The process involves:

1. Setting up a PostgreSQL database in a Docker container.
2. Reading the content of the `.sql` file to populate the PostgreSQL database.
3. Using Python and the Qdrant API to extract embedding vectors from PostgreSQL and upload them to the Qdrant database.

## Steps

1. **Set up PostgreSQL in Docker**:
   - Use a `docker-compose.yml` file to configure and run a PostgreSQL container.

2. **Load the `.sql` file**:
   - Import the `.sql` file into the PostgreSQL database.

3. **Upload to Qdrant**:
   - Use a Python script to:
     - Connect to the PostgreSQL database.
     - Extract embedding vectors.
     - Upload the vectors to Qdrant using the Qdrant API.

## Tools and Libraries

- [Docker](https://www.docker.com/)
- [Qdrant API](https://qdrant.tech/)
- Python libraries:
  - `psycopg2` for PostgreSQL interaction.
  - `qdrant-client` for Qdrant API integration.

## Usage

1. Start the PostgreSQL container:
   ```sh
   docker-compose up -d

2. Run the import_data script
   ```sh
   sh scripts/import_data.sh

3. Run the python script create a new collection in Qdrant and upload the data to it
   ```sh
    docker exec -it <python-container-name> python upload_vectors.py \
    --api-key <your-api-key> \
    --ip-address <qdrant-ip-address> \
    --collection-name <collection-name> \
    --vector-distance <vector-distance>
