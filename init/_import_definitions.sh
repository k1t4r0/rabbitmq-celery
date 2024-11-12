#!/bin/bash

# definitions.sh
echo "Waiting for RabbitMQ to start..."
until curl -s -u Admin:admin http://localhost:15672/api/aliveness-test/%2F > /dev/null 2>&1; do
    sleep 5
done

echo "RabbitMQ is up - importing definitions..."
curl -i -u Admin:admin -H "Content-Type: application/json" -X POST \
     -d @/docker-entrypoint-initdb.d/definitions.json \
     http://localhost:15672/api/definitions

echo "Definitions imported"