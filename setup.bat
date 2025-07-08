@echo off
SETLOCAL ENABLEEXTENSIONS
TITLE Vo&Pet Setup Script for Windows

echo Checking for Docker...

where docker >nul 2>&1
IF ERRORLEVEL 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

where docker-compose >nul 2>&1
IF ERRORLEVEL 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose.
    exit /b 1
)

echo ✅ Docker and Compose are available

IF NOT EXIST .env (
    echo 🛠 Creating .env file...
    echo DEBUG=True>>.env
    echo SECRET_KEY=replace-this-in-production>>.env
    echo POSTGRES_DB=postgres>>.env
    echo POSTGRES_USER=postgres>>.env
    echo POSTGRES_PASSWORD=postgres>>.env
    echo ALLOWED_HOSTS=localhost,127.0.0.1>>.env
)

echo 🐳 Building Docker containers...
docker-compose up --build -d

echo 🧱 Applying migrations and collecting static...
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py compilemessages

set /p create_superuser=Do you want to create a superuser now? [y/n]: 
if /i "%create_superuser%"=="y" (
    docker-compose exec web python manage.py createsuperuser
)

set /p run_tests=Do you want to run tests now? [y/n]: 
if /i "%run_tests%"=="y" (
    docker-compose exec web pytest
)

echo ✅ Setup complete. Open http://localhost:8000 in your browser!
