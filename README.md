Silver Price Ledger System

Requirements

Before running the project, make sure the following are installed:

- Python 3.11+
- Docker
- Docker Compose

1. Clone the Project

git clone <repository-url>
cd Silver-Price-Ledger

2. Create Virtual Environment

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate

3. Install Dependencies

Install the required packages:

pip install -r requirements.txt

4. Configure Environment Variables

The project uses environment variables for database and authentication configuration.

First, create a ".env" file in the project root by copying ".env.example".

On Windows:

copy .env.example .env

Then open the ".env" file and check or modify the values if necessary.

Example:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=silver_price_db

SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5435/silver_price_db

JWT_SECRET_KEY=your_secret_key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

The ".env" file must not be committed to Git.

5. Start PostgreSQL

Start the PostgreSQL container:

docker compose up -d

Make sure the PostgreSQL container is running before continuing.

6. Run Database Migrations

Apply the database migrations:

alembic upgrade head

7. Run the Application

Start the FastAPI application:

uvicorn app.main:app --reload

Alternatively:

fastapi dev

The application will be available at:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs

8. Train Prediction Models

Before using the prediction endpoint, the machine learning models must be trained and generated.

Run the project's model training process using the training method defined in the project.

After successful training, the model files will be stored in:

ml_models/

9. Run Tests

Tests use a separate PostgreSQL database.

First, create ".env.test" by copying ".env.test.example".

On Windows:

copy .env.test.example .env.test

Then run the automated tests:

pytest

Or run them with more detailed output:

pytest -v

10. Stop PostgreSQL

When the application is no longer needed, the PostgreSQL container can be stopped with:

docker compose down