import socket
import threading
from queue import Queue
import time

# Host and Port
HOST = "0.0.0.0"
PORT = 5000

# Global things
job_queue = Queue()            # To hold jobs
jobs_status = {}               # Dictionary to store job status
jobs_result = {}               # Dictionary to store job results
job_id_counter = 1             # start with job 1
lock = threading.Lock()        # Lock for thread safety

def handle_client(conn, addr):
    global job_id_counter
    print(f"[SERVER] Client connected from {addr}")
    
    while True:
        try:
            # receive message and remove newline
            msg = conn.recv(1024).decode().strip()
            
            if not msg:
                break
                
            if msg.startswith("SUBMIT"):
                # like "SUBMIT hello world"
                parts = msg.split(" ", 1)
                
                with lock:
                    job_id = job_id_counter
                    job_id_counter += 1
                    
                    # save status
                    jobs_status[job_id] = "PENDING"
                    jobs_result[job_id] = None
                    
                # add to queue
                job_queue.put((job_id, parts[1]))
                print(f"[SERVER] Given Job {job_id}: {parts[1]}")
                
                # reply to client
                conn.send((f"JOB_ID {job_id}\n").encode())
                
            elif msg.startswith("GET_RESULT"):
                # like "GET_RESULT 1"
                parts = msg.split()
                job_id = int(parts[1])
                
                with lock:
                    if job_id in jobs_status and jobs_status[job_id] == "COMPLETED":
                        res = jobs_result[job_id]
                        conn.send((f"RESULT {job_id} {res}\n").encode())
                    else:
                        conn.send("NOT_READY\n".encode())
                        
        except Exception as e:
            print("[SERVER] Client error")
            break
            
    conn.close()
    print(f"[SERVER] Client {addr} disconnected")


def handle_worker(conn, addr):
    print(f"[SERVER] Worker connected from {addr}")
    
    while True:
        try:
            msg = conn.recv(1024).decode().strip()
            
            if not msg:
                break
                
            if msg == "GET_JOB":
                # check if queue has jobs
                if not job_queue.empty():
                    job_id, job_data = job_queue.get()
                    
                    with lock:
                        jobs_status[job_id] = "ASSIGNED"
                        
                    # send to worker
                    conn.send((f"JOB {job_id} {job_data}\n").encode())
                else:
                    # tell worker no job
                    conn.send("NO_JOB\n".encode())
                    
            elif msg.startswith("DONE"):
                # like "DONE 1 result_text"
                parts = msg.split(" ", 2)
                job_id = int(parts[1])
                result_text = parts[2]
                
                with lock:
                    jobs_status[job_id] = "COMPLETED"
                    jobs_result[job_id] = result_text
                    
                print(f"[SERVER] Job {job_id} is completed!")
                conn.send("ACK\n".encode())
                
        except Exception as e:
            print("[SERVER] Worker disconnected unexpectedly")
            break
            
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # prevent address already in use error
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind((HOST, PORT))
    server.listen(5)
    
    print("[SERVER] Server started on port 5000...")
    
    while True:
        conn, addr = server.accept()
        
        try:
            # get the role from connection
            role = conn.recv(1024).decode().strip()
            
            if role == "CLIENT":
                conn.send("WELCOME\n".encode())
                t = threading.Thread(target=handle_client, args=(conn, addr))
                t.daemon = True
                t.start()
                
            elif role == "WORKER":
                conn.send("WELCOME\n".encode())
                t = threading.Thread(target=handle_worker, args=(conn, addr))
                t.daemon = True
                t.start()
                
        except:
            print("[SERVER] Error during connection setup")
            conn.close()

if __name__ == "__main__":
    start_server()