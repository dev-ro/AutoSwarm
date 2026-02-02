import time
from datetime import datetime

def main():
    duration = 30
    interval = 5
    start_time = time.time()
    
    print(f"Script started at: {datetime.now()}")
    
    # Loop until the duration has passed
    elapsed = 0
    while elapsed < duration:
        time.sleep(interval)
        print(f"Current timestamp: {datetime.now()}")
        elapsed = time.time() - start_time

if __name__ == "__main__":
    main()