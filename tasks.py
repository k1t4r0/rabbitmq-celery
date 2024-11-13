from celery_app import celery
import time


@celery.task(bind=True,name="add_numbers")
def add_numbers(self,x, y):
    """Simply add two numbers."""
    return x + y

@celery.task(bind=True,name="longrun_add_numbers")
def longrun_add_numbers(self,x, y,max_range = 21):
    """
    Perform a long-running calculation.
    Sleeps for 5 seconds initially, then 20 more intervals of 5 seconds each.
    This will be used for queue testing.
    """
    print('Starting long-running task - Initial sleep of 5 seconds')
    time.sleep(5)

    for i in range(1, max_range):
        print(f'Continuing long-running task - Iteration {i} (5 seconds each)')
        time.sleep(5)
    return x + y 

@celery.task(bind=True, name="error_prone_task")
def error_prone_task(self, x, y, max_retries=3):
    """
    Perform an intentional error raising for testing retries and DLQ.
    """

    try:
        # Simulate an error
        raise ValueError("Intentional error for testing retries and DLQ.")
    except Exception as exc:
        # Retry the task up to 'max_retries' times with a delay of 5 seconds between retries
        if self.request.retries < max_retries:
            print(f"Retry attempt {self.request.retries + 1} for error_prone_task")
            raise self.retry(exc=exc, countdown=5)
        else:
            print("Max retries reached. Task will be sent to DLQ.")
            raise exc  # Final raise after max retries to move task to DLQ