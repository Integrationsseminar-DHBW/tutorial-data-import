#!/bin/bash

# Variables
CONTAINER_NAME=postgres
DATABASE_NAME=postgres
USERNAME=postgres
INPUT_FILE=data/database_dump.sql

# get current workspace directory
WORKSPACE=$(pwd)

# use sql dump in workspace/data/database_dump.sql
INPUT_FILE=$WORKSPACE/$INPUT_FILE

# reset the database tables
#python3 src/db/reset_database.py

# Import the dump file into the PostgreSQL database
docker exec -i $CONTAINER_NAME pg_restore -U $USERNAME -d $DATABASE_NAME -v < $INPUT_FILE