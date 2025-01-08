queue = []

def enqueue():
  while len(queue) < 5:
    item = input("Enter items to add to queue: \n")
    queue.append(item)
  print(queue)
enqueue()

def dequeue():   # Returns the first item in the queue
  element = queue.pop(0)
  print("dequeue: ", element)
  print(queue)

def peek():   # Returns the first item in the queue without deleting it from the list
  frontElement = queue[0]
  print("Peek: ", frontElement)
  print(queue)

def lenqueue():  # Checks the length of the queue
  length = len(queue)
  print("Length: ", length)
  print(queue)