#!/bin/bash

IMAGE_NAME="my_telegram_bot"
CONTAINER_NAME="telegram_bot"
DB_PATH="$(pwd)/db.db"

start() {
    echo "Building a new Docker image..."
    docker build -t $IMAGE_NAME .
    echo "Stopping and removing existing container if any..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    echo "Starting a new container..."
    docker run -d --name $CONTAINER_NAME -v $DB_PATH:/app/db.db $IMAGE_NAME
    echo "Container started successfully."
}

stop() {
    echo "Stopping the container..."
    docker stop $CONTAINER_NAME
    echo "Removing the container..."
    docker rm $CONTAINER_NAME
    echo "Container stopped and removed successfully."
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
