import time
import datetime

def main():
    start_time = time.time()
    duration = 30
    interval = 5
    
    while (time.time() - start_time) < duration:
        time.sleep(interval)
        print(f"Current timestamp: {datetime.datetime.now()}")

if __name__ == "__main__":
    main()