#!/bin/bash
#
# Cost Data - Comprehensive Deployment Script
# Deploys all components on port 9999
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Deployment configuration
DEPLOY_PORT=9999
APP_NAME="cost-data"
DEPLOY_USER=${DEPLOY_USER:-$(whoami)}
INSTALL_DIR=${INSTALL_DIR:-/opt/cost-data}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cost Data Deployment Script${NC}"
echo -e "${GREEN}Port: $DEPLOY_PORT${NC}"
echo -e "${GREEN}Install Directory: $INSTALL_DIR${NC}"
echo -e "${GREEN}========================================${NC}"

# Function to print step
print_step() {
    echo -e "\n${YELLOW}[STEP]${NC} $1"
}

# Function to print success
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to print error
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

# Check Java
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}')
    print_success "Java found: $JAVA_VERSION"
else
    print_error "Java not found. Please install JDK 17 or higher."
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python3 not found. Please install Python 3.6 or higher."
    exit 1
fi

# Check Maven
if command -v mvn &> /dev/null; then
    MVN_VERSION=$(mvn --version | head -n 1)
    print_success "Maven found: $MVN_VERSION"
else
    print_error "Maven not found. Please install Maven 3.6 or higher."
    exit 1
fi

# Create installation directory
print_step "Creating installation directory..."
if [ ! -d "$INSTALL_DIR" ]; then
    sudo mkdir -p "$INSTALL_DIR"
    print_success "Created $INSTALL_DIR"
else
    print_success "Directory $INSTALL_DIR already exists"
fi

# Create costdata user if it doesn't exist
print_step "Setting up deployment user..."
if ! id -u costdata &>/dev/null; then
    sudo useradd -r -s /bin/bash -d "$INSTALL_DIR" -c "Cost Data Application" costdata
    print_success "Created costdata user"
else
    print_success "User costdata already exists"
fi

# Set ownership
sudo chown -R costdata:costdata "$INSTALL_DIR"
print_success "Directory ownership set to costdata"

# Build Spring Boot application
print_step "Building Spring Boot application..."
mvn clean package -DskipTests
if [ $? -eq 0 ]; then
    print_success "Spring Boot application built successfully"
else
    print_error "Failed to build Spring Boot application"
    exit 1
fi

# Copy application files
print_step "Copying application files..."
JAR_FILE=$(find target -name "*.jar" -type f | head -n 1)
if [ -z "$JAR_FILE" ]; then
    print_error "No JAR file found in target directory"
    exit 1
fi
sudo cp "$JAR_FILE" "$INSTALL_DIR/cost-data.jar" || {
    print_error "Failed to copy JAR file"
    exit 1
}

if [ -d "src/main/resources" ]; then
    sudo cp -r src/main/resources "$INSTALL_DIR/" || print_error "Warning: Failed to copy resources directory"
fi

for script in server_manager.py demo.py security_news.py requirements.txt; do
    if [ -f "$script" ]; then
        sudo cp "$script" "$INSTALL_DIR/" || print_error "Warning: Failed to copy $script"
    fi
done

sudo chown -R costdata:costdata "$INSTALL_DIR"
print_success "Application files copied to $INSTALL_DIR"

# Create uploads directory
print_step "Creating uploads directory..."
sudo mkdir -p "$INSTALL_DIR/uploads"
sudo chown costdata:costdata "$INSTALL_DIR/uploads"
print_success "Uploads directory created"

# Create data directory for server manager
print_step "Creating data directory..."
sudo mkdir -p "$INSTALL_DIR/data"
sudo chown costdata:costdata "$INSTALL_DIR/data"
print_success "Data directory created"

# Install systemd service
print_step "Installing systemd service..."
if [ -f "deploy/cost-data.service" ]; then
    sudo cp deploy/cost-data.service /etc/systemd/system/
    sudo systemctl daemon-reload
    print_success "Systemd service installed"
else
    print_error "Service file not found, skipping systemd installation"
fi

# Configure firewall
print_step "Configuring firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow $DEPLOY_PORT/tcp
    print_success "UFW firewall rule added for port $DEPLOY_PORT"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=$DEPLOY_PORT/tcp
    sudo firewall-cmd --reload
    print_success "Firewalld rule added for port $DEPLOY_PORT"
else
    print_error "No firewall detected (ufw or firewalld). Please configure manually."
fi

# Create deployment info file
print_step "Creating deployment info..."
cat > "$INSTALL_DIR/deployment-info.txt" << EOF
Cost Data Deployment Information
=================================
Deployment Date: $(date)
Port: $DEPLOY_PORT
Install Directory: $INSTALL_DIR
Deploy User: costdata

Components Deployed:
- Spring Boot File Management Application (port $DEPLOY_PORT)
- Python Server Management System
- Demo Scripts
- Security News System

Service Management:
  Start:   sudo systemctl start cost-data
  Stop:    sudo systemctl stop cost-data
  Status:  sudo systemctl status cost-data
  Enable:  sudo systemctl enable cost-data (auto-start on boot)

Access:
  API: http://localhost:$DEPLOY_PORT/api
  Health: http://localhost:$DEPLOY_PORT/actuator/health

Default Users:
  User: user / password
  Admin: admin / admin
EOF
print_success "Deployment info created"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nTo start the application:"
echo -e "  sudo systemctl start cost-data"
echo -e "\nTo enable auto-start on boot:"
echo -e "  sudo systemctl enable cost-data"
echo -e "\nTo check status:"
echo -e "  sudo systemctl status cost-data"
echo -e "\nApplication will be available at:"
echo -e "  http://localhost:$DEPLOY_PORT"
echo -e "\nFor more information, see:"
echo -e "  cat $INSTALL_DIR/deployment-info.txt"
