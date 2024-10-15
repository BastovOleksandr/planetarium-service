"# planetarium-service" 
# Planetarium API Service 🌌

This Django REST Framework (DRF) powered API facilitates a planetarium service, enabling the management of astronomy shows, themes, and show sessions. It features endpoints for creating and listing show themes and planetarium domes, as well as retrieving and filtering astronomy shows based on titles and themes. Users can reserve tickets for specific show sessions, with built-in pagination for efficient ticket management. The API also includes admin functionalities for uploading show images and managing session details, ensuring a comprehensive and user-friendly experience in the realm of astronomy education and entertainment.

#### If necessary, you can use the following data for authentication (responses to queries may vary depending on role):
admin@admin.com
####
admin
#### or
user@user.com
####
user

## How to run

1. **Clone repository**
```shell
git clone https://github.com/BastovOleksandr/planetarium-service
cd planetarium-service
```
2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv
```
3. **Activate the virtual environment:**
- On Windows:
    ```bash
    venv\Scripts\activate
    ```
- On Unix or MacOS:
    ```bash
    source venv/bin/activate
    ```
4. **Install dependencies:**
```shell
pip install -r requirements.txt
```
5. **Apply migrations:**
```shell
python manage.py migrate
```
6. **Fill the database with prepared fixtures (you can skip the next step after this and use the previously mentioned credentials):**
```bash
python manage.py loaddata fixture.json
```
7. **Create a superuser account:**
```bash
python manage.py createsuperuser
```
8. **You are ready to run your server**
```shell
python manage.py runserver
```

## Run with Docker (Requires the Docker installed on your machine)

1. **Clone repository**
```shell
git clone https://github.com/BastovOleksandr/planetarium-service
cd planetarium-service
```
2. **Rename ".env.sample" file to ".env" in the projects root directory and fill it with necessary data (more info inside the file)**
3. **Build and run docker containers**
```shell
docker-compose up --build
```
5. **After a successful launch, the application will be available at the same address. http://localhost:8000**

## Usage
* Planetarium endpoints: Retrieve and manage planetarium information.
* User endpoints: User registration, login, and token authentication.
* Hint - use http://localhost:8000/api/doc/swagger/ to see all endpoints

## Features
* JWT Authentication
* Admin panel /admin
* Swagger documentation
* Creating planetarium domes, astronomy show themes, astronomy shows, astronomy shows sessions
* Creating and managing reservations and tickets
* Filtering astronomy shows by date and show id
