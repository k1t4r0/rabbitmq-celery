from celery import Celery
from kombu import Queue, Exchange

# Initialize the Celery app
celery = Celery(
    'test_app',
    broker='pyamqp://Admin:admin@127.0.0.1',                # RabbitMQ as the message broker
    backend='redis://127.0.0.1:6379/0'                      # Redis as the result backend
)

# Celery configuration
celery.conf.update(
    {
        # Celery configuration
        'worker_prefetch_multiplier': 1,                    # Number of tasks each worker fetches at once
        #'task_time_limit': 600,                             # Task execution time limit (10 minutes)
        'task_time_limit': 60,                              # Task execution time limit (1 minute for testing)
        'result_expires': 604800,                           # Expire task results after one week
        'broker_pool_limit': 0,                             # Unlimited broker connections
        'task_default_retry_delay': 30,                      # Retry delay in seconds
        'task_max_retries': 3,                              # Maximum retries before sending to DLQ
        'include': ['tasks'],                               # Ensure tasks are loaded by Celery

        # RabbitMQ broker configuration
        'task_acks_late': True,                             # Acknowledge task only after processing
        'task_track_started': True,                         # Track when tasks are received but not started
        'task_reject_on_worker_lost': True,                 # Requeue task if the worker crashes
        'task_acks_on_failure_or_timeout': False,           # Requeue on failure without acknowledgment
        'task_queue_max_priority': 10,                      # Set task priorities (0 = lowest, 10 = highest)

        # Broker transport options for RabbitMQ
        'broker_transport_options': {
            #'visibility_timeout': 600                       # 10 minutes for tasks to be requeued if unacknowledged
            'visibility_timeout': 60,                       # 1 minute, for test purposes
            'max_retries': 5,                               # Retry up to 5 times on connection errors
            'interval_start': 0,                            # Start with no delay
            'interval_step': 2,                             # Increase delay by 2 seconds each retry
            'interval_max': 10,                             # Max retry delay of 10 seconds
        }
    }
)

# Define the queues and exchange as per the RabbitMQ configuration
celery.conf.task_queues = [
    Queue(
        'stg_start_queue.fifo',
        Exchange('dlx_exchange', type='direct', durable=True),
        routing_key='stg_start_queue.fifo',
        queue_arguments={
            'x-queue-type': 'classic',
            'x-max-priority': 10,
            'x-dead-letter-exchange': 'dlx_exchange',      # DLX for retries
            'x-dead-letter-routing-key': 'stg_start_queue.fifo',
            'x-message-ttl': 86400000                      # 24 hours TTL
        }
    ),
    Queue(
        'stg_end_queue.fifo',
        Exchange('dlx_exchange', type='direct', durable=True),
        routing_key='stg_end_queue.fifo',
        queue_arguments={
            'x-queue-type': 'classic',
            'x-max-priority': 10,
            'x-dead-letter-exchange': 'dlx_exchange',
            'x-dead-letter-routing-key': 'stg_end_queue.fifo',
            'x-message-ttl': 86400000
        }
    ),
    Queue(
        'stg_start_queue_dlq',
        Exchange('dlx_exchange', type='direct', durable=True),
        routing_key='stg_start_queue.fifo',
        queue_arguments={
            'x-queue-type': 'classic',
            'x-queue-mode': 'lazy'                         # Lazy mode to reduce memory usage
        }
    ),
    Queue(
        'stg_end_queue_dlq',
        Exchange('dlx_exchange', type='direct', durable=True),
        routing_key='stg_end_queue.fifo',
        queue_arguments={
            'x-queue-type': 'classic',
            'x-queue-mode': 'lazy'
        }
    )
]

# Import tasks after Celery is initialized to avoid circular import
import tasks  # Import the tasks module

celery.register_task(tasks.add_numbers)
celery.register_task(tasks.longrun_add_numbers)
#celery.register_task(tasks.error_prone_task)

if __name__ == '__main__':
    from tasks import add_numbers, longrun_add_numbers, error_prone_task
    celery.start()