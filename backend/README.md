# Big Data Optimizer Backend

This is the **backend** for the Big Data Optimizer project.  
It provides RESTful APIs and background processing for uploading, optimizing, and analyzing large datasets.

---

## 🚀 Getting Started

### 1. **Clone the repository and enter the backend folder**

```bash
git clone https://github.com/yourusername/big-data-optimizer.git
cd big-data-optimizer/backend
```

### 2. **Set up a virtual environment and install dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. **Configure Environment Variables**

Create a `.env` file in the `backend/` directory with your settings (MongoDB URI, etc.) check the file `.env.example`:

```
MONGODB_URI=mongodb://localhost:27017
UPLOAD_DIR=uploads
WORKER_SECONDS_TIME=7
# Add other environment variables as needed
```

---

## 🖥️ Running the API Server

Start the FastAPI server with:

```bash
uvicorn app.main:app --reload
```

- The API will be available at [http://localhost:8000](http://localhost:8000)
- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚙️ Running the Async Worker

The async worker processes background jobs (such as file ingestion, batch processing, and type changes).

Start the worker in a separate terminal:

```bash
cd backend
source venv/bin/activate
python python -m app.workers.async_worker
```

- You can run multiple workers in parallel for higher throughput.
- The worker will poll the jobs queue and process tasks asynchronously.

---

## 🗂️ Project Structure

- `app/main.py` — FastAPI entry point
- `app/utils/` — Utility modules (processing, validation, monitoring, etc.)
- `app/workers/async_worker.py` — Background job processor
- `app/database.py` — MongoDB connection and index management
- `uploads/` — Directory for uploaded files (configurable)

---

## 🛠️ Features

- **Async REST API** for managing repositories and processing jobs
- **Batch processing** for large CSV files
- **Dynamic index management** for efficient queries
- **Background job queue** for heavy or long-running tasks
- **Resource monitoring** and logging

---

## 📝 Customization

- Adjust batch sizes, worker intervals, and other settings via environment variables.
- Extend or modify utility functions in `app/utils/` as needed.

---

## 🧪 Testing

You can add and run tests using your preferred Python testing framework (e.g., pytest).

---

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/en/stable/)
- [Big Data Optimizer Frontend](../frontend/README.md)

---

## 🤝 Contributing

Pull requests and feedback are welcome!  
Please open an issue or submit a PR if you have suggestions or improvements.

---

## License

This project is licensed under the MIT License.