# Silver Price Ledger System

## Requirements

Before running the project, make sure the following software is installed:

* Python 3.11 or higher
* Git
* Docker Desktop
* Docker Compose

---

## 1. Install Python

Python 3.11 or higher is required to run this project.

Download Python from the official Python website:

[Download Python](https://www.python.org/downloads/?utm_source=chatgpt.com)

For Windows, download the latest Python 3.11+ installer.

During installation, **make sure the following option is enabled**:

```text
Add Python.exe to PATH
```

Then continue with the installation.

After installation, open a new **Command Prompt** or **PowerShell** window and check the installation:

```powershell
python --version
```

The output should be similar to:

```text
Python 3.11.x
```

If the `python` command is not recognized, restart the terminal and check again. If the problem remains, make sure Python was added to the system PATH.

---

## 2. Install Git

Git is required to download the project from GitHub.

Download Git for Windows from the official website:

[Download Git for Windows](https://git-scm.com/install/windows?utm_source=chatgpt.com)

After opening the installer, you can use the default installation options. For a normal installation, there is usually no need to change the default settings.

After installation, open a **new** Command Prompt or PowerShell window and check that Git is installed correctly:

```powershell
git --version
```

The output should be similar to:

```text
git version 2.x.x
```

If the `git` command is not recognized, close and reopen the terminal. If the problem continues, restart Windows and try again.

---

## 3. Install Docker Desktop

Docker Desktop is required to run the PostgreSQL databases used by the project.

Download Docker Desktop from the official website:

[Download Docker Desktop](https://www.docker.com/products/docker-desktop/?utm_source=chatgpt.com)

Download the Windows version and complete the installation using the default options.

After installation, **open Docker Desktop and make sure it is running** before continuing.

To verify Docker installation, open a new PowerShell or Command Prompt window and run:

```powershell
docker --version
```

Then check Docker Compose:

```powershell
docker compose version
```

Both commands should display their installed versions.

> Docker Desktop must be running whenever you want to start the PostgreSQL containers.

---

## 4. Clone the Project

Git is used to download the project from GitHub.

Open **PowerShell** or **Command Prompt** and navigate to the folder where you want to store the project.

Then run:

```powershell
git clone https://github.com/Hamedhp05/Silver_price_ledger_and_prediction.git
```

After the download is complete, enter the project directory:

```powershell
cd Silver_price_ledger_and_prediction
```

All remaining commands in this README should be executed from the project root directory unless stated otherwise.

---

## 5. Create Virtual Environment

A virtual environment keeps the Python packages of this project separate from other Python projects on the computer.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

After successful activation, `(.venv)` should appear at the beginning of the terminal prompt.

For example:

```text
(.venv) PS C:\...\Silver_price_ledger_and_prediction>
```

---

## 6. Install Dependencies

With the virtual environment activated, install all required Python packages:

```powershell
pip install -r requirements.txt
```

Wait until the installation finishes successfully before continuing.

---

## 7. Configure Environment Variables

The project uses environment variables for database and authentication configuration.

Create a `.env` file in the project root by copying `.env.example`:

```powershell
copy .env.example .env
```

Then open the `.env` file and check or modify the values if necessary.

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=silver_price_db

SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5435/silver_price_db

JWT_SECRET_KEY=your_secret_key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The `.env` file contains configuration values and must not be committed to Git.

---

## 8. Start PostgreSQL

The project uses PostgreSQL as its database.

Make sure **Docker Desktop is running**, then start the PostgreSQL container:

```powershell
docker compose up -d
```

To check that the container is running:

```powershell
docker ps
```

The PostgreSQL container should appear in the list of running containers.

---

## 9. Run Database Migrations

After starting PostgreSQL, apply the database migrations:

```powershell
alembic upgrade head
```

This creates and updates the required database tables according to the project's migration files.

---

## 10. Run the Application

Make sure the virtual environment is activated, then start the FastAPI application:

```powershell
uvicorn app.main:app --reload
```

The application will be available at:

http://127.0.0.1:8000

Swagger API documentation is available at:

http://127.0.0.1:8000/docs

> Keep this terminal running while using the application.

---
## 11. Authentication and Admin Access

The project uses JWT-based authentication.

When the application starts for the first time, the required price sources and a default administrator account are automatically created in the database.

### Default Administrator Account

The default administrator account is:

```text
Username: admin
Password: 123456
```

> **Important:** This is the default password provided for initial access. For a real production environment, the password should be changed to a secure password.

### Login and Access Token

To access protected endpoints, you must first log in to the application using the administrator account.

You can perform the login through the Swagger API documentation:

http://127.0.0.1:8000/docs

Find the login endpoint and enter:

```text
Username: admin
Password: 123456
```

After a successful login, the API returns an **access token**.

This access token is used to authenticate requests to protected endpoints.

In Swagger, click the **Authorize** button and enter the access token according to the authentication format requested by the API.

After authorization, Swagger will automatically include the access token in requests to protected endpoints.

### Admin-Only Price Collection

The project includes an endpoint for manually starting the price collection process:

```text
POST /collector/run
```

This endpoint is restricted to administrators and cannot be accessed by regular users.

To run it:

1. Log in using the administrator account.
2. Copy the access token returned by the login endpoint.
3. Click **Authorize** in Swagger.
4. Enter the access token.
5. Open the `POST /collector/run` endpoint.
6. Click **Execute**.

If the operation is successful, the API returns:

```json
{
    "message": "Price collection completed successfully."
}
```

The endpoint collects the latest silver prices from the configured data sources.

> **Important:** Authentication is required before accessing protected endpoints. Regular users do not have administrator permissions and cannot execute the price collection endpoint.

## 12. Prediction Models

Pre-trained machine learning models are already included in the project in the following directory:

```text
ml_models/
```

Therefore, it is not necessary to train the models before the first run of the project.

The existing model files can be used directly by the prediction functionality.

### Retraining the Models

If you want to train the models again using the latest data stored in the database, you can run the training process manually.

Open:

```text
app/prediction/training.py
```

At the bottom of the file, the following code is currently commented:

```python
# from app.database.session import SessionLocal
# db = SessionLocal()
# train_models(db)
```

Remove the comments from these lines:

```python
from app.database.session import SessionLocal

db = SessionLocal()
train_models(db)
```

Then, from the root directory of the project, run:

```powershell
python -m app.prediction.training
```

The training process will use the data available in the database and generate the trained model files again inside:

```text
ml_models/
```

After successful training, the newly generated model files will be used by the prediction functionality.

> The PostgreSQL database must be running and contain sufficient data before starting the training process.

---

## 13. Run Tests

The project uses a **separate PostgreSQL database for testing** so that running tests does not affect the main application database.

The test database is defined in:

```text
docker-compose.test.yml
```

### Start the Test Database

First, make sure Docker Desktop is running.

Then start the test PostgreSQL container:

```powershell
docker compose -f docker-compose.test.yml up -d
```

Check that the test database container is running:

```powershell
docker ps
```

After the test database is running, create the test environment file:

```powershell
copy .env.test.example .env.test
```

Then run the tests:

```powershell
pytest
```

For more detailed output:

```powershell
pytest -v
```

### Stop the Test Database

After finishing the tests, the test PostgreSQL container can be stopped with:

```powershell
docker compose -f docker-compose.test.yml down
```

---

## 14. Stop PostgreSQL

When the application is no longer needed, stop the main PostgreSQL container:

```powershell
docker compose down
```
