#!/bin/bash
# ==============================================================================
# Script: restore_rds_guide.sh
# Purpose: This is a guide/interactive script to show how an RDS restore 
#          is performed. It does NOT automatically overwrite your production DB.
# ==============================================================================

echo "================================================================"
echo "🛡️  AWS RDS Restore Guide (InvenioRDM)"
echo "================================================================"
echo "This script prints the exact commands needed to restore an RDS"
echo "snapshot to a new database instance for recovery testing."
echo ""

# 1. Fetch latest snapshot
echo "🔍 Finding latest automated or manual snapshots..."
LATEST_SNAPSHOT=$(aws rds describe-db-snapshots \
    --query 'sort_by(DBSnapshots, &SnapshotCreateTime)[-1].DBSnapshotIdentifier' \
    --output text)

if [ -z "$LATEST_SNAPSHOT" ] || [ "$LATEST_SNAPSHOT" == "None" ]; then
    echo "❌ No snapshots found."
    exit 1
fi

echo "📸 Latest Snapshot found: $LATEST_SNAPSHOT"
echo ""

# 2. Print restore commands
NEW_DB_ID="invenio-recovery-test-$(date +%s)"

echo "💡 TO RESTORE THIS SNAPSHOT TO A NEW INSTANCE, RUN:"
echo "----------------------------------------------------------------"
echo "aws rds restore-db-instance-from-db-snapshot \\"
echo "    --db-instance-identifier $NEW_DB_ID \\"
echo "    --db-snapshot-identifier $LATEST_SNAPSHOT \\"
echo "    --db-instance-class db.t4g.micro \\"
echo "    --publicly-accessible"
echo "----------------------------------------------------------------"
echo ""
echo "⚙️  POST-RESTORE STEPS:"
echo "1. Wait for the new RDS instance to become 'available'."
echo "2. Update your Terraform variables (if using a staging workspace) to point"
echo "   to this new database, OR update the RDS_DB_HOST in your ECS Task Definitions."
echo "3. Restart the InvenioRDM ECS Tasks (web-ui and web-api)."
echo "4. Connect to the web-ui container and rebuild the OpenSearch index:"
echo "   > invenio index destroy --yes-i-know"
echo "   > invenio index init"
echo "   > invenio rdm-records rebuild-index"
echo "================================================================"
