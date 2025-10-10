# scenarios/no-space-left/Dockerfile
FROM alpine:3.18

# Install basic tools including e2fsprogs for mkfs.ext4
RUN apk add --no-cache \
    bash \
    coreutils \
    findutils \
    procps \
    e2fsprogs

# Create a small filesystem with limited inodes (1000 inodes total)
RUN dd if=/dev/zero of=/tmp/small_fs.img bs=1M count=10 && \
    mkfs.ext4 -N 1000 /tmp/small_fs.img && \
    mkdir -p /mnt/small_fs

# Create the inode-filling script
COPY fill_inodes.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/fill_inodes.sh

WORKDIR /app

# Expose nothing - this is a system troubleshooting scenario
# Start with bash and keep container running
CMD ["/bin/bash", "-c", "tail -f /dev/null"]