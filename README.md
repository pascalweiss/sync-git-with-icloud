# sync-icloud-git

[![Pipeline Status](https://git.pwlab.dev/homelab/sync-icloud-git/badges/main/pipeline.svg)](https://git.pwlab.dev/homelab/sync-icloud-git/-/pipelines)
[![Coverage Report](https://git.pwlab.dev/homelab/sync-icloud-git/badges/main/coverage.svg)](https://git.pwlab.dev/homelab/sync-icloud-git/-/jobs)

Automatically sync files from iCloud Drive to a Git repository using rclone and git operations.

## 🚀 Quick Start

1. **Install the package:**
   ```bash
   pip install sync-icloud-git
   ```

2. **Create configuration file:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (see Configuration below)
   ```

3. **Run the sync:**
   ```bash
   source .env
   sync-icloud-git --step sync
   ```

## 📦 Installation

### Prerequisites
- **Python 3.10+** 
- **Git** - For repository operations
- **rclone** - For iCloud connectivity
  ```bash
  curl -fsSL https://rclone.org/install.sh | bash
  ```

### Install from PyPI
```bash
pip install sync-icloud-git
```

### Install from Source
```bash
git clone <repository-url>
cd sync-icloud-git
pip install -e .
```

### Docker Installation
```bash
docker pull registry.pwlab.dev/sync-icloud-to-git:0.1.1
```

## ⚙️ Configuration

Create a `.env` file with your credentials:

```bash
# Git Configuration
SYNC_ICLOUD_GIT__GIT_REMOTE_URL=https://github.com/yourusername/your-repo.git
SYNC_ICLOUD_GIT__GIT_USERNAME=yourusername
SYNC_ICLOUD_GIT__GIT_PAT=your_personal_access_token
SYNC_ICLOUD_GIT__GIT_REPO_PATH=/path/to/local/repo
SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE="Sync from iCloud"

# iCloud Configuration (rclone WebDAV)
SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT="[iclouddrive]
type = webdav
url = https://p123-caldav.icloud.com
user = your-icloud-email@icloud.com
pass = your-app-specific-password"

# Sync Configuration
SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER=Documents/YourFolder
```

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SYNC_ICLOUD_GIT__GIT_REMOTE_URL` | Git repository URL | `https://github.com/user/repo.git` |
| `SYNC_ICLOUD_GIT__GIT_USERNAME` | Git username | `yourusername` |
| `SYNC_ICLOUD_GIT__GIT_PAT` | Git Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `SYNC_ICLOUD_GIT__GIT_REPO_PATH` | Local repository path | `/tmp/my-repo` |
| `SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT` | rclone config for iCloud | See configuration example above |
| `SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER` | iCloud folder to sync | `Documents/MyFolder` |

## 🖥️ CLI Usage

### Basic Commands

```bash
# Sync files from iCloud to Git
sync-icloud-git --step sync

# Run complete workflow (sync + commit + push)
sync-icloud-git --step all

# Test iCloud connection only
sync-icloud-git --step test

# Verbose output for debugging
sync-icloud-git --step sync --verbose
```

### Available Steps

- `sync` - Sync files from iCloud to local repository
- `clone` - Clone repository only
- `update` - Update existing repository only
- `all` - Run complete workflow (sync → commit → push)

### Docker Usage

```bash
# Run with environment file
docker run --env-file .env registry.pwlab.dev/sync-icloud-to-git:0.1.1 --step sync

# Run complete workflow
docker run --env-file .env registry.pwlab.dev/sync-icloud-to-git:0.1.1 --step all
```

## 🔧 Development

### Running Tests
```bash
pip install -e .[dev]
pytest tests/ --verbose --cov=sync_icloud_git
```

### Building Docker Image
```bash
./run/docker_build.sh
```

## 📋 Features

- **Automated iCloud sync** via rclone WebDAV
- **Git integration** with automatic commits and pushes
- **Flexible workflow** - run individual steps or complete pipeline
- **Docker support** for containerized execution
- **Comprehensive logging** with optional verbose mode
- **Pattern-based exclusions** for unwanted files
- **Robust error handling** and validation

## 🛠️ Troubleshooting

### Common Issues

**iCloud Connection Failed:**
- Verify your app-specific password is correct
- Check the WebDAV URL matches your iCloud region
- Ensure 2FA is enabled on your Apple ID

**Git Authentication Failed:**
- Verify your Personal Access Token has repo permissions
- Check the repository URL is correct and accessible

**rclone Not Found:**
- Install rclone: `curl -fsSL https://rclone.org/install.sh | bash`
- Ensure rclone is in your PATH

## Testing

The project includes comprehensive test suites for all modules. See [TESTING.md](TESTING.md) for detailed testing documentation.

### Quick Testing

```bash
# Run all tests
./run/test_all.sh
```

### Test Coverage

- **91% coverage** for configuration module
- **82% coverage** for git operations module
- **97% coverage** for iCloud operations module
- Comprehensive unit tests for all components
- Automated test runners with coverage reporting

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
