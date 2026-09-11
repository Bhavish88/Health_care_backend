
# Healthcare Backend API

A Django REST Framework backend application built for a healthcare system. It provides endpoints for user authentication using JWT, patient management, doctor management, and patient-doctor mappings with PostgreSQL database storage.

## Tech Stack
- Python 3.10+
- Django 5.x
- Django REST Framework (DRF)
- PostgreSQL
- SimpleJWT (`djangorestframework-simplejwt`)
- python-dotenv

---

## Project Structure
```text
Health_care/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── healthcare_project/         # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── authentication/             # Custom User model & JWT login/register
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── patients/                   # Patient records (scoped to authenticated user)
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── doctors/                    # Doctor profiles
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
└── mappings/                   # Patient-Doctor assignments
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── tests.py
```

---

## Database Models & Relationships
- **User**: Custom user model with `email` (unique identifier for login), `name`, and hashed password.
- **Patient**: Fields include `name`, `age`, `gender`, `contact_number`, `medical_history`, and `created_by` (Foreign Key to User). Authenticated users can only view, update, and delete patients they created.
- **Doctor**: Fields include `name`, `specialization`, `email` (unique), `phone`, and `experience_years`.
- **PatientDoctorMapping**: Foreign Keys to `Patient` and `Doctor`. Contains a unique constraint on `(patient, doctor)` to prevent assigning the same doctor to a patient multiple times.

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```ini
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run migrations
Make sure PostgreSQL is running and the database `healthcare_db` is created, then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the server
```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`.

---

## API Endpoints

### 1. Authentication
All protected routes require the header `Authorization: Bearer <access_token>`.

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Public | Register user (`name`, `email`, `password`) |
| `POST` | `/api/auth/login/` | Public | Login with email/password; returns JWT access and refresh tokens |

#### Register Request Body:
```json
{
  "name": "Dr. Sarah Connor",
  "email": "sarah@example.com",
  "password": "Password123"
}
```

#### Login Response:
```json
{
  "message": "Login successful.",
  "tokens": {
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>"
  },
  "user": {
    "id": 1,
    "name": "Dr. Sarah Connor",
    "email": "sarah@example.com"
  }
}
```

---

### 2. Patients
Users can only view and manage patient records that they created.

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/patients/` | Authenticated | Add a new patient |
| `GET` | `/api/patients/` | Authenticated | List all patients created by current user |
| `GET` | `/api/patients/<id>/` | Authenticated | Get details of a specific patient |
| `PUT` | `/api/patients/<id>/` | Authenticated | Update patient details |
| `DELETE` | `/api/patients/<id>/` | Authenticated | Delete a patient |

#### Patient Request Body:
```json
{
  "name": "John Doe",
  "age": 35,
  "gender": "Male",
  "contact_number": "1234567890",
  "address": "123 Main St",
  "medical_history": "No known allergies"
}
```

---

### 3. Doctors

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/doctors/` | Authenticated | Add a new doctor |
| `GET` | `/api/doctors/` | Authenticated | List all doctors |
| `GET` | `/api/doctors/<id>/` | Authenticated | Get details of a specific doctor |
| `PUT` | `/api/doctors/<id>/` | Authenticated | Update doctor details |
| `DELETE` | `/api/doctors/<id>/` | Authenticated | Delete a doctor |

#### Doctor Request Body:
```json
{
  "name": "Gregory House",
  "specialization": "Diagnostic Medicine",
  "email": "house@hospital.com",
  "phone": "9876543210",
  "experience_years": 15
}
```

---

### 4. Patient-Doctor Mappings

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/mappings/` | Authenticated | Assign a doctor to a patient |
| `GET` | `/api/mappings/` | Authenticated | List all patient-doctor mappings |
| `GET` | `/api/mappings/<patient_id>/` | Authenticated | Get all doctors assigned to a patient |
| `DELETE` | `/api/mappings/<id>/` | Authenticated | Remove a doctor from a patient (delete mapping) |

#### Assign Doctor Request Body:
```json
{
  "patient": 1,
  "doctor": 1,
  "notes": "Regular consultation"
}
```

---

## Running Tests
To run the automated test suite:
```bash
python manage.py test
```
All 25 test cases verify authentication, permissions, CRUD functionality, user isolation, and mapping constraints.

