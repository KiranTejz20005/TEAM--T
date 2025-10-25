#!/bin/bash

# FinMDA-Bot Setup Script
# This script sets up the complete FinMDA-Bot environment

set -e

echo "🚀 Setting up FinMDA-Bot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if required environment variables are set
check_env_vars() {
    print_status "Checking environment variables..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY is not set. Please set it in your environment or .env file"
    else
        print_success "OPENAI_API_KEY is set"
    fi
    
    if [ -z "$AWS_ACCESS_KEY_ID" ]; then
        print_warning "AWS_ACCESS_KEY_ID is not set. Optional for S3 storage"
    fi
    
    if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        print_warning "AWS_SECRET_ACCESS_KEY is not set. Optional for S3 storage"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/uploads
    mkdir -p backend/chromadb
    mkdir -p backend/data
    mkdir -p backend/logs
    mkdir -p frontend/build
    mkdir -p nginx/ssl
    
    print_success "Directories created"
}

# Copy environment files
setup_env_files() {
    print_status "Setting up environment files..."
    
    if [ ! -f backend/.env ]; then
        cp backend/env.example backend/.env
        print_success "Created backend/.env from template"
    else
        print_warning "backend/.env already exists"
    fi
    
    if [ ! -f frontend/.env ]; then
        cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
EOF
        print_success "Created frontend/.env"
    else
        print_warning "frontend/.env already exists"
    fi
}

# Install system dependencies (for Ubuntu/Debian)
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Update package list
    sudo apt-get update
    
    # Install required packages
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        nodejs \
        npm \
        postgresql-client \
        redis-tools \
        curl \
        wget \
        git \
        build-essential \
        libpq-dev \
        tesseract-ocr \
        tesseract-ocr-eng \
        libtesseract-dev \
        poppler-utils \
        ghostscript \
        libgs-dev
    
    print_success "System dependencies installed"
}

# Build and start Docker containers
start_services() {
    print_status "Building and starting Docker containers..."
    
    # Build images
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    print_success "Docker containers started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    until docker-compose exec -T postgres pg_isready -U finmda_user -d finmda_bot; do
        sleep 2
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for Backend
    print_status "Waiting for Backend API..."
    until curl -f http://localhost:8000/api/v1/health; do
        sleep 5
    done
    print_success "Backend API is ready"
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    until curl -f http://localhost:3000; do
        sleep 5
    done
    print_success "Frontend is ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    docker-compose exec backend alembic upgrade head
    
    print_success "Database migrations completed"
}

# Install Python dependencies locally (for development)
install_python_deps() {
    print_status "Installing Python dependencies locally..."
    
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    
    print_success "Python dependencies installed"
}

# Install Node.js dependencies locally (for development)
install_node_deps() {
    print_status "Installing Node.js dependencies locally..."
    
    cd frontend
    npm install
    cd ..
    
    print_success "Node.js dependencies installed"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Backend tests
    docker-compose exec backend pytest tests/ -v
    
    print_success "Tests completed"
}

# Display service URLs
show_urls() {
    print_success "FinMDA-Bot is now running!"
    echo ""
    echo "🌐 Service URLs:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:   http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/docs"
    echo "  Flower:       http://localhost:5555"
    echo "  Nginx:        http://localhost:80"
    echo ""
    echo "📊 Monitoring:"
    echo "  Health Check: http://localhost:8000/api/v1/health"
    echo "  Service Status: http://localhost:8000/api/v1/status"
    echo ""
    echo "🔧 Management Commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Rebuild:      docker-compose up --build"
}

# Main setup function
main() {
    echo "🎯 FinMDA-Bot Setup Script"
    echo "========================="
    echo ""
    
    # Check prerequisites
    check_docker
    check_env_vars
    
    # Setup environment
    create_directories
    setup_env_files
    
    # Install dependencies
    if [ "$1" = "--install-deps" ]; then
        install_system_deps
        install_python_deps
        install_node_deps
    fi
    
    # Start services
    start_services
    wait_for_services
    run_migrations
    
    # Run tests if requested
    if [ "$1" = "--test" ]; then
        run_tests
    fi
    
    # Show final status
    show_urls
    
    print_success "Setup completed successfully! 🎉"
}

# Run main function with arguments
main "$@"
