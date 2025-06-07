#!/usr/bin/env python3
"""
Concise working test of rclone_python with real credentials.
Proves rclone_python works without subprocess fallback.
Requires that .env is sourced
"""
import os
import tempfile
from rclone_python import rclone

def test_rclone_sync():
    """Test rclone_python sync with real environment credentials."""
    
    # Get config from environment
    config_content = os.getenv('SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT')
    if not config_content:
        print("❌ ERROR: SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT not found")
        print("Run: source .env")
        return False
    
    # Create temp config file
    config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
    config_file.write(config_content)
    config_file.flush()
    config_file.close()
    
    try:
        print("🚀 Testing rclone_python...")
        
        # Sync using correct parameters (KEY DISCOVERY: src_path/dest_path)
        rclone.sync(
            src_path="iclouddrive:tmp",
            dest_path="/tmp/rclone_test",
            args=['--config', config_file.name, '-v'],
            show_progress=True
        )
        
        print("✅ SUCCESS! rclone_python works perfectly")
        
        # Check results
        os.makedirs("/tmp/rclone_test", exist_ok=True)
        files = []
        for root, dirs, filenames in os.walk("/tmp/rclone_test"):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        
        print(f"📁 Synced {len(files)} files:")
        for file_path in files:
            rel_path = os.path.relpath(file_path, "/tmp/rclone_test")
            size = os.path.getsize(file_path)
            print(f"   📄 {rel_path} ({size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
        
    finally:
        os.unlink(config_file.name)

if __name__ == "__main__":
    success = test_rclone_sync()
    print(f"🎯 Test {'PASSED' if success else 'FAILED'}")
