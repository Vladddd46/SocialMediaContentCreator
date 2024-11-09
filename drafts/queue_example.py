import queue
import threading
import time

# Create a queue for inter-thread communication
data_queue = queue.Queue()


# Define the producer thread (sending data)
def producer():
    for i in range(5):
        item = f"Message {i}"
        print(f"Producer: putting {item} in queue")
        data_queue.put(item)  # Add data to the queue
        time.sleep(1)


# Define the consumer thread (receiving data)
def consumer():
    while True:
        item = data_queue.get()  # Waits for data to become available
        print(f"Consumer: got {item} from queue")
        data_queue.task_done()  # Signal that the task is complete


# Start the producer and consumer threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer, daemon=True)

producer_thread.start()
consumer_thread.start()

# Wait for the producer to finish
producer_thread.join()

# Wait until the queue is empty before exiting
data_queue.join()
print("All items processed.")
