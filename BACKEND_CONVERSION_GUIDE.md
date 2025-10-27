# Guide: Converting Your Python Script to a Web Backend

This document is your step-by-step guide to transforming the `guardian_agent_simple.py` script into a scalable, robust backend for a web application. The goal here is not just to give you instructions, but to help you learn the core concepts of backend development. As such, this guide will explain the "what" and the "why," and will provide links to official documentation for you to explore and implement the "how."

---

## Introduction: From a Script to a Service

Your current script is a **synchronous command-line application**. When you run it, it performs all its tasks in a single, continuous process and then exits. A web backend, however, is a **persistent, asynchronous service**. It must be able to handle multiple requests from different users at the same time, manage long-running processes without crashing, and maintain state between requests.

Our journey will involve building three core components:

1.  **API Layer:** The "front door" of your backend that listens for HTTP requests from a web browser.
2.  **Task Queue:** A system for managing long-running jobs (like a code audit) in the background.
3.  **Database:** A persistent storage system to keep track of tasks and their results.

Let's begin.

---

## Part 1: The API Layer with FastAPI

Your backend needs a way to listen for and respond to requests over the internet. This is the job of a web framework. We'll use **FastAPI** because it's modern, extremely fast, and its built-in data validation makes development much easier.

### Concepts to Understand:

*   **What is an API?** An Application Programming Interface (API) is a set of rules that allows different software applications to communicate with each other. In our case, it's how your frontend (the website) will talk to your backend (this service).
*   **Endpoints:** These are specific URLs in your API that correspond to certain actions. For example, you'll create an endpoint at a URL like `/api/v1/audit` that the frontend can send a request to in order to start a new audit.
*   **HTTP Methods:** These are the types of requests a client can make. The most common are `GET` (to retrieve data), `POST` (to submit new data), `PUT` (to update existing data), and `DELETE` (to remove data). Your "start audit" endpoint will use `POST`.
*   **Data Validation with Pydantic:** How do you ensure the frontend sends the correct data (e.g., a valid URL)? FastAPI uses a library called Pydantic to define the expected "shape" of your data. If a request doesn't match this shape, FastAPI automatically returns a clear error.

### Your Implementation Steps:

1.  **Install FastAPI and an ASGI Server:** FastAPI requires a server program to run it. `uvicorn` is the standard choice.
2.  **Create Your Main Application File:** You will create a new Python file (e.g., `main.py`) where you will instantiate your main FastAPI application object.
3.  **Define Your First Endpoint:** Create a function that will handle requests to `/api/v1/audit`. You will decorate this function to mark it as a `POST` endpoint.
4.  **Define Your Data Schema:** Using Pydantic, create a class that defines the data you expect in a request to start an audit (e.g., a field for `repo_url`).
5.  **Run the Server:** Use `uvicorn` from your terminal to run your application. You'll now have a running web server!

**📚 Essential Reading:**

*   **FastAPI Official Tutorial:** [Start with "First Steps" and read through "Path Parameters" and "Request Body."](https://fastapi.tiangolo.com/tutorial/first-steps/) This is one of the best tutorials in all of open source.
*   **Pydantic Documentation:** [Understand the basics of creating schemas.](https://docs.pydantic.dev/latest/concepts/models/)

---

## Part 2: Background Tasks with Celery & Redis

A code audit can take minutes. If you run this audit directly inside your API endpoint function, the web request will be stuck waiting and eventually time out. This is a terrible user experience. We need to run these jobs in the background.

### Concepts to Understand:

*   **Asynchronous Tasks:** These are tasks that are run outside of the immediate request-response cycle.
*   **Task Queue (or Message Broker):** This is a system that holds a list of "jobs" that need to be done. Your API will add a job to the queue, and a separate process will pick it up and execute it. **Redis** is a popular, high-performance choice for a message broker.
*   **Task Worker:** This is a separate Python process whose only job is to watch the queue for new tasks, execute them, and report the results. **Celery** is the most widely-used library for creating task queues and workers in Python.
*   **The Producer/Consumer Pattern:** Your FastAPI application is the **Producer** (it creates tasks and adds them to the queue). Your Celery worker is the **Consumer** (it consumes tasks from the queue and executes them).

### Your Implementation Steps:

1.  **Install Celery and Redis:** You'll need to add Celery to your project and have a Redis server running (you can easily run one with Docker).
2.  **Configure Celery:** Create a new file to configure Celery and tell it where to find your Redis server.
3.  **Create a Task Function:** In a new file (e.g., `tasks.py`), you will define a function that contains the core logic of your audit (i.e., the `agent.run()` call). You will decorate this function with `@celery.task`.
4.  **Modify Your API Endpoint:** Instead of calling `agent.run()` directly, your `/api/v1/audit` endpoint will now call your Celery task function using `.delay()`. This adds the job to the queue and immediately returns a response to the user, usually with a unique `task_id`.
5.  **Run the Celery Worker:** From your terminal, you will start the Celery worker process. It will connect to Redis and wait for jobs to appear.

**📚 Essential Reading:**

*   **Celery - First Steps with Celery:** [This is the official guide to getting a basic task queue running.](https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html)
*   **Redis Documentation:** [An introduction to what Redis is.](https://redis.io/docs/about/)

---

## Part 3: Managing State with a Database

Your application is no longer a single-run script. It needs to remember things. Where is the report for `task_id: xyz-123`? What was the status of that task? An in-memory variable won't work because your web server and Celery worker are different processes and can be restarted. You need a database.

### Concepts to Understand:

*   **Persistence:** The ability of your application to save data in a way that survives when the application is shut down.
*   **Relational Database:** A structured database like **PostgreSQL** or **SQLite**. It's excellent for storing well-defined data like task IDs, statuses, creation times, and user information.
*   **ORM (Object-Relational Mapper):** An ORM like **SQLAlchemy** allows you to interact with your database using Python classes and objects instead of writing raw SQL queries. This makes your code cleaner, safer, and more maintainable.

### Your Implementation Steps:

1.  **Choose and Install a Database:** For development, **SQLite** is the easiest as it's just a single file. For production, **PostgreSQL** is a more robust choice.
2.  **Install SQLAlchemy:** Add SQLAlchemy to your project's dependencies.
3.  **Define Your Database Models:** In a new `models.py` file, you will create Python classes that represent your database tables. For example, you might create an `AuditTask` class with fields like `id`, `task_id`, `repo_url`, `status`, `created_at`, and `result_path`.
4.  **Integrate with Your Application:**
    *   In your API endpoint, when a new task is created, you will create a new `AuditTask` object and save it to the database with a status of "PENDING".
    *   In your Celery task, you will update the status of the task in the database to "RUNNING" when it starts, and "COMPLETED" or "FAILED" when it finishes. You will also save the path to the final JSON report in the database.
5.  **Create Status Endpoints:** You will create new API endpoints, like `GET /api/v1/audit/status/{task_id}`, that query the database to fetch and return the status of a task.

**📚 Essential Reading:**

*   **SQLAlchemy ORM Tutorial:** [This guide will show you how to define models and query your database using the ORM pattern.](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
*   **FastAPI with a Database:** [The official FastAPI documentation has an excellent section on integrating with SQLAlchemy.](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

## Part 4: Project Restructuring

To accommodate all these new components, you need a clean and scalable project structure.

### Your New Directory Structure:

A good structure separates concerns, making the project easier to navigate and maintain.

```
/guardian-backend
|-- /app
|   |-- __init__.py
|   |-- main.py          # FastAPI application and API endpoints.
|   |-- tasks.py         # Celery task definitions.
|   |-- agent_core.py    # Your refactored GuardianAgent logic.
|   |-- db.py            # Database session management.
|   |-- models.py        # SQLAlchemy database models.
|   |-- schemas.py       # Pydantic data schemas for the API.
|-- celery_worker.py     # The entry point to run the Celery worker.
|-- requirements.txt
|-- .env                 # For storing environment variables (like API keys).
```

### Your Implementation Steps:

1.  Create the new directory structure.
2.  Move the core logic from `guardian_agent_simple.py` into `app/agent_core.py`.
3.  Remove all command-line parsing logic (`argparse`) from the agent. The agent should be a simple Python class that can be imported and used by other parts of your application.
4.  Set up your `requirements.txt` file with all the new libraries (fastapi, uvicorn, celery, redis, sqlalchemy, etc.).

---

## Part 5: Essential Web Concepts

Finally, there are two web-specific challenges you'll need to solve.

### 1. Handling File Uploads

Your original script reads a PDF from the local filesystem. In a web app, the user needs to upload this file from their browser.

*   **Concept:** Your API endpoint will need to handle `multipart/form-data` requests.
*   **Implementation:** FastAPI has a specific type hint (`UploadFile`) for handling file uploads. Your endpoint will receive the file, save it to a temporary location, and then pass that file path to the Celery task.

**📚 Essential Reading:**

*   **FastAPI - File Uploads:** [The official documentation for handling uploaded files.](https://fastapi.tiangolo.com/tutorial/request-files/)

### 2. CORS (Cross-Origin Resource Sharing)

For security reasons, web browsers block requests from a web page to a different domain (or "origin") than the one that served the page. If your frontend is at `www.my-app.com` and your backend is at `api.my-app.com`, the browser will block the request unless your backend explicitly allows it.

*   **Concept:** CORS is a mechanism that uses HTTP headers to tell a browser that it's okay for a web application at one origin to access resources from a server at a different origin.
*   **Implementation:** FastAPI provides a `CORSMiddleware` that you can easily add to your application to configure which origins are allowed to access your API.

**📚 Essential Reading:**

*   **FastAPI - CORS:** [The official documentation for enabling and configuring CORS.](https://fastapi.tiangolo.com/tutorial/cors/)

---

## Conclusion

By following this guide, you will have deconstructed your script and rebuilt it into a true web service. You will have learned about APIs, background processing, database management, and core web principles. Take it one step at a time, read the documentation carefully, and focus on understanding the "why" behind each component. Good luck!
