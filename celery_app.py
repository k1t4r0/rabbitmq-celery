from celery import Celery
from kombu import Queue, Exchange

# Initialize the Celery app
celery = Celery(
    'test_app',
    broker='pyamqp://Test:test@127.0.0.1',                # RabbitMQ as the message broker
    backend='redis://127.0.0.1:6379/0'                      # Redis as the result backend
)

# Celery configuration
celery.conf.update(
    {
        # Celery configuration
        'worker_prefetch_multiplier': 1,                    # Number of tasks each worker fetches at once
        'task_time_limit': 600,                             # Task execution time limit (10 minutes)
        #'task_time_limit': 60,                              # Task execution time limit (1 minute for testing)
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
        
        'task_create_missing_queues': False,                 # Avoid creating missing queues in RabbitMQ

        # Broker transport options for RabbitMQ
        'broker_transport_options': {
            'visibility_timeout': 600,                       # 10 minutes for tasks to be requeued if unacknowledged
            #'visibility_timeout': 60,                       # 1 minute, for test purposes
            'max_retries': 5,                               # Retry up to 5 times on connection errors
            'interval_start': 0,                            # Start with no delay
            'interval_step': 2,                             # Increase delay by 2 seconds each retry
            'interval_max': 10,                             # Max retry delay of 10 seconds
        },

        'task_default_queue': 'stg_start_queue.fifo',       # Set default queue

        # Define task routes for specific queues
        'task_routes': {
            'tasks.add_numbers': {'queue': 'stg_start_queue.fifo'},
            'tasks.longrun_add_numbers': {'queue': 'stg_end_queue.fifo'},
            'tasks.error_prone_task': {'queue': 'stg_start_queue.fifo'},
        },

        # Define task_queues without additional arguments to register with Celery
        # 'task_queues': [
        #     Queue('stg_start_queue.fifo',passive=True),
        #     Queue('stg_end_queue.fifo',passive=True),
        # ]
        'task_queues': [
            Queue(
                'stg_start_queue.fifo',
                Exchange('default', type='direct'),
                routing_key='stg_start_queue.fifo',
                durable=True,
                max_priority=10,
                queue_arguments={
                    'x-message-ttl': 86400000,  # Match the existing TTL in milliseconds
                    'x-max-priority': 10,
                    'x-dead-letter-exchange': 'dlx_exchange',  # Include if used in RabbitMQ
                    'x-dead-letter-routing-key': 'stg_start_queue.fifo',  # Include if used
                    'x-queue-type': 'classic',  # Include if specified in RabbitMQ
                }
            ),
            Queue(
                'stg_end_queue.fifo',
                Exchange('default', type='direct'),
                routing_key='stg_end_queue.fifo',
                durable=True,
                max_priority=10,
                queue_arguments={
                    'x-message-ttl': 86400000,
                    'x-max-priority': 10,
                    'x-dead-letter-exchange': 'dlx_exchange',
                    'x-dead-letter-routing-key': 'stg_end_queue.fifo',
                    'x-queue-type': 'classic',
                }
            ),
        ]         
    }
)



# Import tasks after Celery is initialized to avoid circular import
# import tasks  # Import the tasks module

# celery.register_task(tasks.add_numbers)
# celery.register_task(tasks.longrun_add_numbers)
#celery.register_task(tasks.error_prone_task)

if __name__ == '__main__':
    # from tasks import add_numbers, longrun_add_numbers, error_prone_task
    celery.start()