# Getting Started

Get your PraetorAPI project up and running in minutes.

## 1. Environment Setup

```bash
# Clone and enter the project
git clone <repo_url>
cd praetor-api

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initial configuration
cp .env.example .env
```

## 2. Initialize Database & Security

```bash
# Apply migrations
python manage.py db:migrate

# Create an Admin user
python manage.py auth:createsuperuser

# Generate initial system permissions
python manage.py auth:makepermissions
```

## 3. The Development Loop

### Step 1: Generate a Feature
```bash
# Create an app (domain)
python manage.py make:app store

# Create an entity (module)
python manage.py make:entity product --app store
```

### Step 2: Run the APIs
```bash
python manage.py run:server
```

## 4. Frontend Integration

PraetorAPI comes with a professional **React + Vite + Tailwind** frontend.

```bash
cd web
npm install
npm run dev
```

### Fullstack Power
When you run `make:entity`, the system automatically generates:
1.  **Backend logic**: models, routers, and services.
2.  **Frontend views**: A complete **DataTable** with CRUD actions.
3.  **Automatic Routing**: The new page is instantly visible in the Sidebar menu.

## 5. Deployment with Docker

To run the entire ecosystem (API, Postgres, Redis, Celery, Frontend) in a production-ready environment:

```bash
docker-compose up --build
```
