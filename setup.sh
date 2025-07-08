#!/bin/bash

set -e

echo "🔍 Checking Docker & Docker Compose..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Generate .env if not exists
if [ ! -f ".env" ]; then
    echo "🛠 Creating .env file..."
    cat <<EOF > .env
DEBUG=True
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    echo "✅ .env file created"
fi

echo "🐳 Building Docker containers..."
docker-compose up --build -d

echo "🧱 Applying migrations and collecting static..."
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py compilemessages

echo "✅ App is now running at http://localhost:8000"

read -p "➕ Do you want to create a superuser now? [y/n]: " create_superuser
if [[ "$create_superuser" == "y" ]]; then
    docker-compose exec web python manage.py createsuperuser
fi

read -p "🧪 Do you want to run tests now? [y/n]: " run_tests
if [[ "$run_tests" == "y" ]]; then
    docker-compose exec web pytest
fi  

echo "✅ Setup complete. Happy coding 🎓"

