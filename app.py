from tasks import add_numbers, longrun_add_numbers, error_prone_task

class App:
    def __init__(self):
        print("App initialized to send tasks to 'stg_start_queue.fifo'.")

    def add_numbers_task(self, x, y):
        """Send add_numbers task to the queue."""
        result = add_numbers.apply_async(args=(x, y), queue='stg_start_queue.fifo')
        print(f"add_numbers task sent to queue with task ID: {result.id}")
        return result

    def longrun_add_numbers_task(self, x, y, max_range=21):
        """Send longrun_add_numbers task to the queue."""
        result = longrun_add_numbers.apply_async(args=(x, y, max_range), queue='stg_start_queue.fifo')
        print(f"longrun_add_numbers task sent to queue with task ID: {result.id}")
        return result

    def error_prone_task_task(self, x, y, max_retries=3):
        """Send error_prone_task to the queue to test retries and DLQ."""
        result = error_prone_task.apply_async(args=(x, y, max_retries), queue='stg_start_queue.fifo')
        print(f"error_prone_task sent to queue with task ID: {result.id}")
        return result

# Example usage
if __name__ == "__main__":
    app = App()
    app.add_numbers_task(3, 4)
    app.longrun_add_numbers_task(5, 6)
    # app.error_prone_task_task(7, 8)
