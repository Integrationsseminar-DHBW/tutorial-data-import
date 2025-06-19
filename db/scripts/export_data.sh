#!/bin/bash

# Variables
CONTAINER_NAME=postgres
DATABASE_NAME=postgres
USERNAME=postgres
OUTPUT_FILE=database_dump.sql
OUTPUT_PATH=data/$OUTPUT_FILE

# Export the data
docker exec -t $CONTAINER_NAME pg_dump -U $USERNAME -d $DATABASE_NAME -F c -b -v -f  /tmp/$OUTPUT_FILE

# Copy the dump file to the local machine
docker cp $CONTAINER_NAME:/tmp/$OUTPUT_FILE $OUTPUT_PATH