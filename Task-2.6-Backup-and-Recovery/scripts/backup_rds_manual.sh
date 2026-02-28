#!/bin/bash
# ==============================================================================
# Script: backup_rds_manual.sh
# Purpose: Triggers a manual AWS RDS snapshot for the InvenioRDM database.
# Note: This supplements the automated 7-day backups already configured in Terraform.
# ==============================================================================

set -e

echo "🔍 Fetching current DB instance identifier..."
# Fetch the RDS instance identifier (assuming 'invenio-default' prefix based on TF)
DB_INSTANCE_ID=$(aws rds describe-db-instances \
    --query 'DBInstances[?starts_with(DBInstanceIdentifier, `invenio-default-rds`)].DBInstanceIdentifier' \
    --output text | head -n 1)

if [ -z "$DB_INSTANCE_ID" ] || [ "$DB_INSTANCE_ID" == "None" ]; then
    echo "❌ Error: Could not find the InvenioRDM RDS instance."
    exit 1
fi

TIMESTAMP=$(date +%Y-%m-%d-%H-%M-%S)
SNAPSHOT_NAME="manual-invenio-backup-${TIMESTAMP}"

echo "📸 Triggering manual snapshot for RDS instance: $DB_INSTANCE_ID"
echo "📦 Snapshot Name: $SNAPSHOT_NAME"

aws rds create-db-snapshot \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --db-snapshot-identifier "$SNAPSHOT_NAME"

echo ""
echo "✅ Snapshot triggered successfully."
echo "⏳ It may take a few minutes to complete. You can check the status with:"
echo "   aws rds describe-db-snapshots --db-snapshot-identifier $SNAPSHOT_NAME --query 'DBSnapshots[0].Status'"
