# 📊 Data Processing & Benchmarking System

## Overview

This project is a high-performance, scalable system designed to process large-scale public datasets (up to 50 million records) using two distinct processing methods:

1. **Basic Processing** – Straightforward linear processing.
2. **Optimized Processing** – Enhanced performance using techniques like batching and parallelism.

### 🎯 Goals

* Compare and benchmark different processing strategies.
* Handle very large datasets without exceeding system limitations.
* Generate batch-wise results and compute final metrics asynchronously.
* Provide a clear and interactive frontend for visualization.

### 🧱 Tech Stack

* **Frontend**: Next.js
* **Backend**: FastAPI
* **Database**: MongoDB
* **Deployment**: Docker + Docker Compose on Ubuntu 24.04

---

# 📂 Project Structure

```
project-root/
│
├── frontend/           # Next.js app
├── backend/            # FastAPI app
├── data/               # Dataset loading and management
├── scripts/            # Batch processing and maintenance jobs
├── docker-compose.yml  # Multi-service container setup
└── README.md           # General project overview (this file)
```

---

# 🚀 How to Run the Project

### Prerequisites

* Docker + Docker Compose
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/Josesebastianaguilar/big-data-optimizer.git
cd big-data-optimizer
```

### 2. Start the System

```bash
docker-compose up --build
```

This will start:

* MongoDB
* FastAPI backend (on port 8000)
* Next.js frontend (on port 3000)

### 3. Access the App

Visit [http://localhost:3000](http://localhost:3000)

---

# 📈 Processing Flow Summary

1. **Upload or select dataset**
2. **Initiate process** (basic / optimized / AI-assisted)
3. **Split into batches (\~10,000 records each)**
4. **Store intermediate batch results**
5. **Compute and display final result from batch results**
6. **Generate PDF / CSV reports**

---

# 📚 Additional Docs

* [Frontend README](./frontend/README.md)
* [Backend README](./backend/README.md)

---

# 📄 License

MIT License – Use freely with attribution

---

# 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you’d like to change.

---

# 📬 Contact

José Aguilar – [jose.aguilar.silva@outlook.com](mailto:jose.aguilar.silva@outlook.com) – GitHub: \(https://github.com/Josesebastianaguilar) 
