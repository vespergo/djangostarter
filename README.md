# Django Starter

## Getting Started

1. **Clone the Repository:**

    ```bash
    git git clone https://github.com/vespergo/djangostarter.git
    cd djangostarter
    ```

2. **Create Virtual Environment:**

    ```bash
    python -m venv venv
    ```

3. **Activate Virtual Environment:**

    On Windows:

    ```bash
    .\venv\Scripts\activate
    ```

    On macOS/Linux:

    ```bash
    source venv/bin/activate
    ```

4. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Run Migrations:**

    ```bash
    python manage.py migrate
    ```

    This will set up the initial database schema.

6. **Load Initial Data:**

    ```bash
    python manage.py loaddata all_models.json
    ```

    This will seed the database with initial data.

## Usage

- Start the Django development server:

    ```bash
    python manage.py runserver
    ```

- Access the application in your web browser at `http://127.0.0.1:800/records/`.
