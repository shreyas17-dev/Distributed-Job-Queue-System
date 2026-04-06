# Distributed Job Queue Service

**Mini-Project:** Distributed Job Queue Service using TCP Socket Programming

## 📌 Project Overview
This project implements a lightweight distributed computing system where a central server distributes tasks to multiple worker nodes. It is built from scratch using raw Python TCP sockets for robust backend communication and features a Flask-based web dashboard.

Using the web dashboard, users can submit background jobs, track their status, and monitor real-time worker activities as they pull tasks from the queue and compute them.

## ✨ Features
* **TCP Socket Communication:** Core networking logic built entirely using raw socket programming (no 3rd-party messaging libraries).
* **Distributed Workers:** Support for spinning up multiple concurrent worker nodes that fetch and process jobs from a shared queue continuously.
* **Client UI:** A web-based interface to easily submit text-based tasks and check their completion status.
* **Admin Dashboard:** A real-time monitoring dashboard to view queue sizes, total job status (Pending, Assigned, Completed), and live tracking of which task each worker is processing.
* **Thread-safe Queueing:** Backed by Python's `queue.Queue` and threading locks to prevent race conditions when multiple workers request jobs simultaneously.

## 🏗️ Architecture Design
The architecture is designed in 3 layers:
1. **Frontend (Web UI)**: Two separate HTML interfaces (`client.html`, `admin.html`) built with HTML/CSS/JS.
2. **Web Wrapper (`app.py`)**: A Flask application that serves the frontend, provides REST APIs to submit jobs, and natively embeds the TCP Socket Server in a background daemon thread.
3. **Compute Nodes (`worker.py`)**: Independent, terminal-based Python processes that connect to the TCP server to perform the heavy lifting.

## 💻 Tech Stack
* **Language:** Python 3.x
* **Networking:** `socket`, `threading`
* **Web Framework:** Flask (for serving UI & API endpoints)
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)

## 📂 Project Structure
```text
├── app.py             # Flask Web App & Main execution file
├── server.py          # Core TCP Server logic & Queue management
├── worker.py          # Worker script (Start multiple instances)
└── templates/
    ├── client.html    # Client UI for job submission
    └── admin.html     # Admin dashboard for monitoring
```

## 🚀 Prerequisites

Before running the application, make sure you have Flask installed:
```bash
pip install flask
```

## 🚀 How to Run the Project

### Step 1: Start the Server (Backend + Web Application)
Open your terminal and run the main entry point:
```bash
python app.py
```
*Note: This will start both the Flask Web UI on `http://localhost:8080` and the hidden TCP Socket Server in the background.*

### Step 2: Spin Up Worker Nodes
Open a **new terminal tab/window** for each worker you want to launch.
```bash
python worker.py
```
*(You can run this command in 2 or 3 separate terminal windows simultaneously to see distributed load-balancing in action).*

### Step 3: Access the Dashboards
Open your preferred web browser and go to:
* **Client Dashboard (Submit Jobs):** [http://localhost:8080](http://localhost:8080)
* **Admin Dashboard (Monitor System):** [http://localhost:8080/admin](http://localhost:8080/admin)

---
### 🧪 Example Usage
1. Open up the Admin dashboard so you can watch live updates.
2. Ensure you have at least 1 or 2 `worker.py` terminal windows running.
3. Open the Client dashboard, type a task (e.g., `"Calculate factors of 9999"`), and hit submit.
4. Watch the Admin dashboard instantly assign the task to an available worker, process it, and return the result.
