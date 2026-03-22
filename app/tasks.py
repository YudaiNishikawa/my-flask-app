import time

def example_task(seconds):
    print("start back job")
    for i in range(seconds):
        print(f"while working..{i+1}/{seconds}seconds")
        time.sleep(1)
    print("finish working")    