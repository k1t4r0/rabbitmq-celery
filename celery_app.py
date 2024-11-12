from celery import Celery

# Initialize the Celery app
celery = Celery(
    'test_app',
    broker='pyamqp://k1t4r0:i74790k_@15.228.51.20',         # RabbitMQ as the message broker
    backend='redis://127.0.0.1:6379/0'                      # Redis as the result backend
)

# Celery configuration
celery.conf.update(
    {
        # Celery configuration
        'worker_prefetch_multiplier': 1,                    # Number of tasks each worker fetches at once
        'task_time_limit': 600,                             # Task execution time limit (10 minutes)
        'result_expires': 604800,                           # Expire task results after one week
        'broker_pool_limit': 0,                             # Unlimited broker connections
        'task_default_retry_delay': 30,                      # Retry delay in seconds
        'task_max_retries': 3,                              # Maximum retries before sending to DLQ

        # RabbitMQ broker configuration
        'task_acks_late': True,                             # Acknowledge task only after processing
        'task_track_started': True,                         # Track when tasks are received but not started
        'task_reject_on_worker_lost': True,                 # Requeue task if the worker crashes
        'task_acks_on_failure_or_timeout': False,           # Requeue on failure without acknowledgment
        'task_queue_max_priority': 10,                      # Set task priorities (0 = lowest, 10 = highest)

        # Broker transport options for RabbitMQ
        'broker_transport_options': {
            'visibility_timeout': 600                       # 10 minutes for tasks to be requeued if unacknowledged
        }
    }
)

# Define main queue with a dead-letter exchange
celery.conf.task_queues = [
    Queue(
        'stg_start_queue.fifo', 
        Exchange('main_exchange'), 
        routing_key='stg_start_queue.fifo', 
        queue_arguments={
            'x-dead-letter-exchange': 'dlx_exchange',         # Define DLX for failed tasks
            'x-dead-letter-routing-key': 'dlq_queue'          # Route failed tasks to DLQ
        }
    ),
    Queue(
        'dlq_queue', 
        Exchange('dlx_exchange'), 
        routing_key='dlq_queue'                               # DLQ for tasks that exceed retry limit
    )
]




if __name__ == '__main__':
    celery.start()
