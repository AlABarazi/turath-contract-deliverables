#!/bin/bash
# ==============================================================================
# Script: backup_s3_manual.sh
# Purpose: Manually syncs the primary InvenioRDM S3 bucket to a local folder 
#          or a secondary S3 bucket for disaster recovery testing.
# ==============================================================================

set -e

# Configuration
# Default to syncing to a local folder, but can be overridden
DESTINATION_DIR=${1:-"./s3_backup_$(date +%Y-%m-%d)"}

# Primary S3 bucket for InvenioRDM data
BUCKET_NAME="turath-inveniordm-data"

echo "🔍 Verifying bucket exists..."
if ! aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    echo "❌ Error: Bucket 's3://$BUCKET_NAME' does not exist or is not accessible."
    exit 1
fi

echo "🪣 Source Bucket: s3://$BUCKET_NAME"
echo "📁 Destination: $DESTINATION_DIR"
echo ""

# Ensure local destination exists if it's a local path
if [[ "$DESTINATION_DIR" != s3://* ]]; then
    mkdir -p "$DESTINATION_DIR"
fi

echo "🔄 Starting S3 Sync (this may take a while depending on file size)..."
aws s3 sync "s3://$BUCKET_NAME" "$DESTINATION_DIR"

echo ""
echo "✅ S3 Backup completed successfully."
