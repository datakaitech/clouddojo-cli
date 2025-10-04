#!/bin/bash
# Fill up inodes using a small filesystem
# This simulates a runaway logging process

echo "=== Inode Exhaustion Simulation ==="
echo "Setting up small filesystem with limited inodes..."

# Check if filesystem is already mounted, if not mount it
if ! mountpoint -q /mnt/small_fs; then
    mount -o loop /tmp/small_fs.img /mnt/small_fs
fi

echo "Initial inode status:"
df -i /mnt/small_fs

echo ""
echo "Simulating runaway log file creation..."
mkdir -p /mnt/small_fs/logs
cd /mnt/small_fs/logs

# Create 1000 files to exhuast inodes
echo "Creating 1000 log files to nearly exhaust inodes..."
for i in {1..1000}; do
    touch "app_${i}.log"
done
