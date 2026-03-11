# OBE Automation Backend

This project handles Outcome-Based Education (OBE) tracking, built with Django. It utilizes **Django Templates** for the frontend, with some components powered by **Vue.js**, which are directly integrated into the templates without needing a standalone Vue frontend server.

It uses **Django Guardian** for Attribute-Based Access Control (ABAC) and built-in permissions for Role-Based Access Control (RBAC).

## Prerequisites
- Python 3.10+
- Django 5.x
- MySQL Server (Optional, standard SQLite is used instead if MySQL is not configured)
- pip

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd OBE-Backend
   ```

2. **Set up Virtual Environment:**
   Create and activate a virtual environment for the project.
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   Install required Python packages, including the database drivers and dotenv for the environment configurations.
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   A template has been provided to set up your local environment file.
   ```bash
   cp .env.example .env
   ```
   **Database Configuration**:
   - By default, if the `.env` settings are absent or if `DB_ENGINE` is missing, the project will safely fall back to using standard SQLite (`db.sqlite3`).
   - If you wish to use MySQL for a robust environment, simply set `DB_ENGINE=django.db.backends.mysql` and update `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` appropriately in your `.env`.

5. **Run Migrations:**
   Ensure all database tables are created.
   ```bash
   python manage.py migrate
   ```

6. **Seed the Database (Optional):**
   To experience the project flow or perform demonstrations out-of-the-box, run the included seeder to populate mock data (users, programs, etc.):
   ```bash
   python manage.py seed_db
   ```
   *This command will generate the following seed accounts:*
   - Admin: **admin** / **admin123**
   - Faculty: **faculty_demo** / **faculty123**
   - Student: **student_demo** / **student123**

7. **Run the Server:**
   Launch the Django development server.
   ```bash
   python manage.py runserver
   ```
   You can now visit `http://127.0.0.1:8000` to interact with the application.

## Integrated Vue.js Components
The frontend architecture contains Vue.js interactions stored natively inside the `static/js/` directory. Since they are imported and accessed dynamically within standard Django templates using CDN script tags or basic static references, you don't need to run tools like `npm run dev` or setup Node.js to see them in action. Ensure `manage.py runserver` is running, then everything serves directly.
