from celery_app import celery
from tasks import add_numbers, longrun_add_numbers, error_prone_task

class App:
    def __init__(self):
        print("App initialized to send tasks to the queues.")

    def add_numbers_task(self, x, y):
        """Send add_numbers task to the queue."""
        print("Sending add_numbers task...")
        # result = add_numbers.apply_async(args=(x, y))
        result = add_numbers.delay(x,y)
        # result = celery.send_task('tasks.add_numbers', args=(x, y))
        print(f"add_numbers task sent with task ID: {result.id}")
        return result

    def longrun_add_numbers_task(self, x, y, max_range=5):
        """Send longrun_add_numbers task to the queue."""
        print("Sending longrun_add_numbers task...")
        # result = longrun_add_numbers.apply_async(args=(x, y, max_range))
        result = longrun_add_numbers.delay(x, y, max_range)
        # result = celery.send_task('tasks.longrun_add_numbers', args=(x, y, max_range))
        print(f"longrun_add_numbers task sent with task ID: {result.id}")
        return result

    def error_prone_task_task(self, x, y, max_retries=3):
        """Send error_prone_task to test retries and DLQ."""
        print("Sending error_prone_task...")
        result = error_prone_task.delay(x, y, max_retries)
        # result = celery.send_task('tasks.error_prone_task', args=(x, y, max_retries))
        print(f"error_prone_task sent with task ID: {result.id}")
        return result

# Example usage
if __name__ == "__main__":
    app = App()
    app.add_numbers_task(3, 4)
    app.longrun_add_numbers_task(5, 6)
    app.error_prone_task_task(7, 8)
