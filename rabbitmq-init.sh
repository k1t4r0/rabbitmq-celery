#!/bin/bash
# This script will run automatically when RabbitMQ starts

# Wait for RabbitMQ to fully initialize
until curl -u Admin:admin -s http://localhost:15672/api/overview; do
  echo "Waiting for RabbitMQ to start..."
  sleep 5
done
echo "RabbitMQ has started."

# Add a new RabbitMQ user
echo "Creating user Admin..."
rabbitmqctl add_user Admin admin
rabbitmqctl set_user_tags Admin administrator
rabbitmqctl set_permissions -p / Admin ".*" ".*" ".*"

# Create the dead-letter exchange
echo "Creating dead-letter exchange..."
curl -u Admin:admin -X PUT -H "Content-Type: application/json" -d'{"type":"direct","auto_delete":false,"durable":true}' http://localhost:15672/api/exchanges/%2f/dlx_exchange

# Create the 'stg_start_queue.fifo' with max priority 10 and dead-letter exchange
echo "Creating stg_start_queue.fifo..."
curl -u Admin:admin -X PUT -H "Content-Type: application/json" -d'{"durable":true,"arguments":{"x-max-priority":10,"x-dead-letter-exchange":"dlx_exchange"}}' http://localhost:15672/api/queues/%2f/stg_start_queue.fifo

# Create the 'stg_end_queue.fifo' with max priority 10 and dead-letter exchange
echo "Creating stg_end_queue.fifo..."
curl -u Admin:admin -X PUT -H "Content-Type: application/json" -d'{"durable":true,"arguments":{"x-max-priority":10,"x-dead-letter-exchange":"dlx_exchange"}}' http://localhost:15672/api/queues/%2f/stg_end_queue.fifo
