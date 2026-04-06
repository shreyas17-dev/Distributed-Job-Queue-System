import socket
import time
import random

HOST = "127.0.0.1"
PORT = 5000

# Connect to server
worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("[WORKER] Connecting...")
worker.connect((HOST, PORT))

# Handshake
worker.send("WORKER\n".encode())
reply = worker.recv(1024).decode().strip()

if reply == "WELCOME":
    print("[WORKER] Connected successfully")
else:
    print("[WORKER] Handshake failed")
    exit()

# Main loop to get jobs
while True:
    try:
        # Ask for a job
        worker.send("GET_JOB\n".encode())
        
        response = worker.recv(1024).decode().strip()
        
        if response == "":
            print("[WORKER] Server disconnected")
            break
            
        if response == "NO_JOB":
            print("[WORKER] No jobs. Sleeping for a bit...")
            time.sleep(3)
            continue
            
        # Parse job details (Format: "JOB 1 hello")
        if response.startswith("JOB"):
            parts = response.split(" ", 2)
            job_id = parts[1]
            job_data = parts[2]
            
            print(f"[WORKER] Got Job {job_id}: {job_data}")
            
            # Simulate hard work (sleep for some seconds)
            work_time = random.randint(2, 5)
            print(f"[WORKER] Working for {work_time} seconds...")
            time.sleep(work_time)
            
            # Process data
            result_data = "ERROR"
            
            job_parts = job_data.split(" ")
            operation = job_parts[0].lower()
            
            try:
                if operation == "factorial":
                    n = int(job_parts[1])
                    ans = 1
                    for i in range(1, n + 1):
                        ans *= i
                    result_data = str(ans)
                    
                elif operation == "addition" or operation == "add":
                    a = int(job_parts[1])
                    b = int(job_parts[2])
                    result_data = str(a + b)
                    
                elif operation == "multiplication" or operation == "multiply":
                    a = int(job_parts[1])
                    b = int(job_parts[2])
                    result_data = str(a * b)
                
                elif operation == "subtraction" or operation == "subtract":
                    a = int(job_parts[1])
                    b = int(job_parts[2])
                    result_data = str(a - b)
                    
                else:
                    # If it's not a math command, just reverse the string
                    result_data = job_data[::-1].upper()
                    
            except Exception as e:
                # If they forgot to pass numbers or passed bad data
                result_data = f"Error performing {operation}"
            
            # Send result back
            worker.send((f"DONE {job_id} {result_data}\n").encode())
            
            ack = worker.recv(1024).decode().strip()
            print(f"[WORKER] Server said: {ack}")
            print("-----------------------")
            
    except Exception as e:
        print(f"[WORKER] Error: {e}")
        break

worker.close()