# Backup and Recovery Scripts (Task 2.6)

This folder contains the functional backup and recovery scripts designed to satisfy disaster recovery testing and manual backup requirements. 

Because the infrastructure is natively hosted on AWS via Terraform, these scripts act as wrappers around the AWS CLI to trigger and verify backups safely.

## Files included:

1. `backup_rds_manual.sh`: 
   - Finds the primary InvenioRDM database.
   - Triggers an immediate, manual AWS RDS Snapshot.
   - Does not interfere with the automated 7-day backup rotation already handled by Terraform.

2. `backup_s3_manual.sh`: 
   - Finds the primary InvenioRDM S3 file storage bucket.
   - Manually `sync`s the bucket to a local directory or a secondary bucket.
   - Useful for taking cold-storage snapshots of PDFs/HOCR files.

3. `restore_rds_guide.sh`: 
   - Safe guide script. Finds the latest valid RDS snapshot and prints the exact AWS CLI commands needed to restore it to a new "Test Host" database instance.
   - Prints the exact post-restore steps required to reconnect InvenioRDM and rebuild the OpenSearch index.

## Usage:
Make sure you are authenticated with AWS (e.g., via `aws-login`) before running these scripts.

```bash
./backup_rds_manual.sh
./backup_s3_manual.sh
./restore_rds_guide.sh
```
