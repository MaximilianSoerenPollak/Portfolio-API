#!bin/bash

CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED
    echo "-- First container startup --"
    # YOUR_JUST_ONCE_LOGIC_HERE
    bash -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 "
else
    echo "-- Not first container startup --"
    bash -c "uvicorn main:app --host 0.0.0.0 --port 8000"
fi