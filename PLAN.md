# Implementation Plan: Backend-Agnostic Cloud Sync

## Objective
Decouple the application from iCloud to support any rclone backend (Nextcloud, Google Drive, Dropbox, S3, etc.) while maintaining backward compatibility for existing iCloud users.

## Approach
Add a configurable `rclone_remote_name` parameter that allows users to specify which rclone remote section to use. This is the minimal change needed since rclone already handles all cloud provider abstractions.

## Changes Required

### 1. Configuration Module (`sync_icloud_git/config.py`)
**Changes:**
- Add `rclone_remote_name` parameter to `SyncConfig.__init__()`
- Add `DEFAULT_RCLONE_REMOTE_NAME = "iclouddrive"` constant (for backward compatibility)
- Add `--rclone-remote-name` CLI argument (optional, defaults to "iclouddrive")
- Add `SYNC_ICLOUD_GIT__RCLONE_REMOTE_NAME` environment variable support
- Update `__repr__()` to include the new parameter

**Rationale:** Existing iCloud users don't need to change anything - it defaults to "iclouddrive"

### 2. Cloud Operations Module (`sync_icloud_git/icloud_operations.py`)
**Changes:**
- Rename class: `ICloudOperations` → `CloudSyncOperations`
- Update `__init__()` to accept `config.rclone_remote_name`
- Update `_build_remote_path()` to use configurable remote name instead of hardcoded "iclouddrive"
- Update docstrings to be backend-agnostic (remove iCloud-specific language)
- Update verbose messages to be generic (e.g., "Cloud sync configured" instead of "iCloud sync configured")
- Rename method: `test_icloud_connection()` → `test_connection()`
- Rename method: `sync_from_icloud_to_repo()` → `sync_from_cloud_to_repo()`
- Keep backward compatibility: Create `test_icloud_connection()` and `sync_from_icloud_to_repo()` as deprecated aliases
- Update `__repr__()` to reflect new class name and parameters
- Rename file: `icloud_operations.py` → `cloud_operations.py`

**Rationale:** Makes the code honest about what it does - sync from any cloud backend

### 3. CLI Module (`sync_icloud_git/cli.py`)
**Changes:**
- Update import: `from sync_icloud_git.cloud_operations import CloudSyncOperations`
- Update `ICloudSyncStep` class name → `CloudSyncStep`
- Update step name: "Syncing from iCloud" → "Syncing from cloud storage"
- Update variable names: `icloud_ops` → `cloud_ops`
- Update success messages to be backend-agnostic
- Add backward compatibility import alias: `ICloudOperations = CloudSyncOperations`

**Rationale:** User-facing messages should be generic

### 4. Tests (`tests/test_icloud_operations.py`)
**Changes:**
- Rename file: `test_icloud_operations.py` → `test_cloud_operations.py`
- Update imports: `from sync_icloud_git.cloud_operations import CloudSyncOperations`
- Update test class: `TestICloudOperations` → `TestCloudOperations`
- Add test for configurable remote name (test with "nextcloud", "gdrive", etc.)
- Add test for default remote name (ensures backward compatibility)
- Update all test fixtures to use new class name
- Add test that verifies backward compatibility aliases work

**Rationale:** Ensure all functionality works with new abstractions

### 5. Documentation Updates
**Files to update:**
- `README.md` - Add Nextcloud example, mention multi-backend support
- `CLAUDE.md` - Update architecture description
- `.env_template` - Add `RCLONE_REMOTE_NAME` example with comments
- Default commit message in config.py: "Sync git with iCloud Drive" → "Sync from cloud storage"

**Rationale:** Users need to know about the new capability

### 6. Backward Compatibility Strategy
**Approach:**
- Default `rclone_remote_name` to "iclouddrive" (no breaking changes for existing users)
- Keep `ICloudOperations` as an alias to `CloudSyncOperations` with deprecation warning
- Keep old method names as aliases with deprecation warnings
- Environment variable prefix stays `SYNC_ICLOUD_GIT__` (no breaking changes)

**Future consideration:** Could rename package in v2.0 to `sync-cloud-git`

## Implementation Order

1. **Step 1:** Update `config.py` - Add new parameter with default
2. **Step 2:** Rename and update `icloud_operations.py` → `cloud_operations.py`
3. **Step 3:** Update `cli.py` to use new class and generic messages
4. **Step 4:** Update tests to match new structure
5. **Step 5:** Update documentation
6. **Step 6:** Run full test suite to ensure 100% compatibility
7. **Step 7:** Manual testing with both iCloud and Nextcloud configs

## Example Configurations

### iCloud (existing users - no changes needed)
```bash
SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT="[iclouddrive]
type = webdav
url = https://p123-caldav.icloud.com
..."
# SYNC_ICLOUD_GIT__RCLONE_REMOTE_NAME defaults to "iclouddrive"
```

### Nextcloud (new users)
```bash
SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT="[nextcloud]
type = webdav
url = https://cloud.example.com
vendor = nextcloud
..."
SYNC_ICLOUD_GIT__RCLONE_REMOTE_NAME="nextcloud"
```

### Google Drive (new capability)
```bash
SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT="[gdrive]
type = drive
client_id = ...
..."
SYNC_ICLOUD_GIT__RCLONE_REMOTE_NAME="gdrive"
```

## Risk Assessment
- **Low risk:** Changes are minimal and backward compatible
- **High test coverage:** 91%+ coverage ensures no regressions
- **Deprecation path:** Old names kept as aliases for smooth migration

## Success Criteria
- [ ] All existing tests pass without modification
- [ ] New tests verify multi-backend support
- [ ] Existing iCloud configs work without changes
- [ ] Nextcloud configuration works as expected
- [ ] Documentation clearly explains new capability
- [ ] No breaking changes for existing users
