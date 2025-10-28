# Git Repository Manager

A comprehensive Python application that manages multiple git repositories and provides API endpoints for project metadata extraction using Tree-sitter. This tool is designed to help build C4 architecture metadata by analyzing codebases and extracting structural information.

## 🚀 Features

- **Repository Management**: Configure multiple git repositories with SSH keys
- **Automatic Synchronization**: Periodic cloning/pulling of repositories (configurable interval)
- **Code Analysis**: Extract project metadata using Tree-sitter parsers
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, C#
- **REST API**: Comprehensive API for project information and entry points
- **Real-time Updates**: Background synchronization with status tracking
- **Docker Support**: Container-ready for easy deployment

## 🛠️ Installation

### Quick Setup

1. **Clone and setup**:
```bash
git clone <repository-url>
cd AicesPlusOne
python setup.py
```

2. **Start the application**:
```bash
python dev_server.py
```

### Manual Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Setup environment**:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

3. **Create directories**:
```bash
mkdir -p repositories data .ssh_keys logs
```

4. **Run the application**:
```bash
python -m aices_plus_one.main
```

### Docker Installation

```bash
docker-compose up -d
```

## 📚 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Core Endpoints

#### Repository Management
- `POST /repositories` - Add a new repository configuration
- `GET /repositories` - List all configured repositories  
- `DELETE /repositories/{repo_id}` - Remove a repository configuration
- `GET /repositories/{repo_id}/sync-status` - Get sync status
- `POST /repositories/sync` - Manually trigger synchronization

#### Project Analysis
- `GET /projects` - List all projects with metadata
- `GET /projects/{project_id}` - Get specific project metadata
- `GET /projects/{project_id}/entrypoints` - Get entry points for a project

#### System
- `GET /health` - Health check endpoint
- `GET /` - API information

## 🔧 Configuration

### Environment Variables

```bash
# Database settings
DATABASE_PATH=repositories.db

# Repository settings  
REPOSITORIES_DIR=repositories

# Synchronization (in minutes)
SYNC_INTERVAL_MINUTES=5

# API settings
API_HOST=0.0.0.0
API_PORT=8000

# Security
SSH_KEYS_DIR=/tmp/git_ssh_keys

# Analysis
CACHE_REFRESH_HOURS=1
MAX_DEPENDENCIES=50

# Logging
LOG_LEVEL=INFO
```

### Repository Configuration Format

```json
{
    "name": "my-project",
    "url": "git@github.com:user/repo.git", 
    "ssh_private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\n...",
    "ssh_public_key": "ssh-ed25519 AAAAC3...",
    "default_branch": "main"
}
```

## 💻 Usage Examples

### Using the Example Client

```bash
# Add a repository
python example_client.py add my-repo git@github.com:user/repo.git ~/.ssh/id_rsa ~/.ssh/id_rsa.pub

# List repositories
python example_client.py list-repos

# List analyzed projects
python example_client.py list-projects

# Get entry points for a project
python example_client.py entrypoints my-repo_project-name

# Trigger manual sync
python example_client.py sync

# Check health
python example_client.py health
```

### Using curl

```bash
# Add repository
curl -X POST "http://localhost:8000/repositories" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "my-repo",
       "url": "git@github.com:user/repo.git",
       "ssh_private_key": "...",
       "ssh_public_key": "...",
       "default_branch": "main"
     }'

# Get projects
curl "http://localhost:8000/projects"

# Get entry points
curl "http://localhost:8000/projects/my-repo_project/entrypoints"
```

## 🏗️ Architecture

### Components

1. **API Layer** (`api.py`): FastAPI-based REST API
2. **Database Layer** (`database.py`): SQLite with async support
3. **Git Manager** (`git_manager.py`): Repository cloning and synchronization
4. **Tree-sitter Analyzer** (`tree_sitter_analyzer.py`): Code analysis and metadata extraction
5. **Scheduler**: Background task for periodic synchronization

### Data Flow

1. Configure repositories via API
2. Background scheduler clones/pulls repositories
3. Tree-sitter analyzes code and extracts metadata
4. API serves project information and entry points
5. External services consume data for C4 architecture building

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Test coverage:
```bash
pip install pytest-cov
python -m pytest tests/ --cov=aices_plus_one --cov-report=html
```

## 📋 Supported Languages & Features

| Language   | Entry Points | Dependencies | Project Type Detection |
|------------|--------------|--------------|----------------------|
| Python     | ✅ Functions, Classes | ✅ requirements.txt, setup.py | ✅ |
| JavaScript | ✅ Functions, Classes | ✅ package.json | ✅ |
| TypeScript | ✅ Functions, Classes | ✅ package.json | ✅ |
| Java       | ✅ Methods, Classes | ✅ pom.xml | ✅ |
| C++        | ⏳ Coming Soon | ⏳ | ✅ |
| Go         | ⏳ Coming Soon | ⏳ | ✅ |
| Rust       | ⏳ Coming Soon | ✅ Cargo.toml | ✅ |
| C#         | ⏳ Coming Soon | ⏳ | ✅ |

### Project Types Detected

- Web Applications
- APIs (FastAPI, Flask, Django, Express, etc.)
- CLI Tools
- Libraries
- Microservices
- Mobile Apps
- Desktop Applications

## 🔒 Security Considerations

- SSH keys are stored securely in the database
- Temporary SSH key files are cleaned up after use
- API doesn't expose private keys in responses
- File system permissions are properly set
- Docker containers run with appropriate security context

## 🚀 Production Deployment

### Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  git-repo-manager:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./repositories:/app/repositories
    environment:
      - DATABASE_PATH=/app/data/repositories.db
      - SYNC_INTERVAL_MINUTES=5
    restart: unless-stopped
```

### Systemd Service

```ini
[Unit]
Description=Git Repository Manager
After=network.target

[Service]
Type=simple
User=git-manager
WorkingDirectory=/opt/git-repo-manager
ExecStart=/opt/git-repo-manager/.venv/bin/python -m aices_plus_one.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**SSH Key Issues**
- Ensure SSH keys have proper permissions (600 for private key)
- Verify SSH key format (OpenSSH format required)
- Check if the key is added to your git provider

**Tree-sitter Parsing Errors**
- Some files may be skipped if they contain syntax errors
- Check logs for specific parsing issues
- Ensure language parsers are properly installed

**Synchronization Issues**
- Check repository URLs and SSH key access
- Verify network connectivity
- Review sync status via API endpoint

### Logs

Application logs are available at:
- Console output (development)
- Container logs (Docker)
- `/app/logs/` directory (if configured)

### Health Check

Use the health endpoint to monitor application status:
```bash
curl http://localhost:8000/health
```
