from flask import Flask, render_template, request, jsonify
import threading
import server  # Directly import the user's unmodified server.py

# ==========================================
# Flask Application Setup
# ==========================================
app = Flask(__name__)

# ==========================================
# Dynamic Injection (Monkey Patching)
# ==========================================
# The original server.py does not track worker IDs or which job they are assigned.
# To obey the rule of NOT modifying server.py, we enhance its logic here dynamically!

active_workers = {} # Format: { "Worker-53421": "Job 5" or "Idle" }

def enhanced_handle_worker(conn, addr):
    worker_id = f"Worker-{addr[1]}"
    active_workers[worker_id] = "Idle"
    print(f"[APP-ENHANCED SERVER] {worker_id} connected from {addr}")
    
    while True:
        try:
            msg = conn.recv(1024).decode().strip()
            
            if not msg:
                break
                
            if msg == "GET_JOB":
                if not server.job_queue.empty():
                    job_id, job_data = server.job_queue.get()
                    
                    with server.lock:
                        server.jobs_status[job_id] = "ASSIGNED"
                        
                    # Track that this worker got the job!
                    active_workers[worker_id] = f"Processing Job {job_id}"
                    
                    conn.send((f"JOB {job_id} {job_data}\n").encode())
                else:
                    conn.send("NO_JOB\n".encode())
                    
            elif msg.startswith("DONE"):
                parts = msg.split(" ", 2)
                job_id = int(parts[1])
                result_text = parts[2]
                
                with server.lock:
                    server.jobs_status[job_id] = "COMPLETED"
                    server.jobs_result[job_id] = result_text
                    
                print(f"[APP-ENHANCED SERVER] Job {job_id} is completed by {worker_id}!")
                
                # Worker is now idle again
                active_workers[worker_id] = "Idle"
                conn.send("ACK\n".encode())
                
        except Exception as e:
            print(f"[APP-ENHANCED SERVER] {worker_id} disconnected")
            break
            
    conn.close()
    if worker_id in active_workers:
        del active_workers[worker_id]

# Override the original function inside the server module before starting it!
server.handle_worker = enhanced_handle_worker


# Start the actual TCP Socket Server
tcp_thread = threading.Thread(target=server.start_server)
tcp_thread.daemon = True
tcp_thread.start()

# ==========================================
# Flask Web Routes
# ==========================================
@app.route("/")
def client_page():
    return render_template("client.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

# ==========================================
# Flask REST APIs reading directly from server.py memory
# ==========================================
@app.route("/api/submit", methods=["POST"])
def submit_job():
    data = request.json
    job_data = data.get("job_data", "")
    
    if not job_data:
        return jsonify({"error": "Empty job data"}), 400
        
    with server.lock:
        job_id = server.job_id_counter
        server.job_id_counter += 1
        
        server.jobs_status[job_id] = "PENDING"
        server.jobs_result[job_id] = None
        
    server.job_queue.put((job_id, job_data))
    
    return jsonify({"job_id": job_id, "status": "PENDING", "job_data": job_data})

@app.route("/api/status/<int:job_id>", methods=["GET"])
def get_status(job_id):
    with server.lock:
        if job_id not in server.jobs_status:
            return jsonify({"error": "Job not found"}), 404
            
        return jsonify({
            "job_id": job_id,
            "status": server.jobs_status[job_id],
            "result": server.jobs_result[job_id]
        })

@app.route("/api/admin/data", methods=["GET"])
def admin_data():
    with server.lock:
        all_jobs = []
        for j_id, status in server.jobs_status.items():
            all_jobs.append({
                "job_id": j_id,
                "status": status,
                "result": server.jobs_result.get(j_id)
            })
            
        return jsonify({
            "queue_size": server.job_queue.qsize(),
            "total_jobs": len(server.jobs_status),
            "jobs": all_jobs,
            "workers": active_workers
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
