# Turath InvenioRDM Backup and Recovery Plan (Task 2.6)

## 1. Introduction

This document outlines the backup and recovery procedures for the Turath InvenioRDM infrastructure hosted on AWS. 

As per the initial requirements, a dedicated "test host" was specified for recovery testing. However, to provide a more robust, enterprise-grade solution, the infrastructure has been implemented using **Terraform (Infrastructure-as-Code)**. In this modern architecture, the "test host" is not a static machine; instead, our recovery testing procedure involves spinning up an identical parallel environment on AWS on-demand, restoring the data, verifying integrity, and tearing it down. This guarantees that our recovery process is tested against the exact configuration used in production.

## 2. Backup Strategy (Stateful Resources)

The system relies on AWS native managed services to ensure continuous, reliable backups for all persistent data stores.

### 2.1 Relational Database (Amazon RDS PostgreSQL)
*This is the core PostgreSQL database holding all InvenioRDM metadata, users, and state.*
- **Mechanism:** AWS RDS Automated Backups.
- **Schedule:** Automated snapshots are taken daily during the maintenance window (`03:00-06:00` UTC).
- **Retention:** Backups are retained for **7 days**.
- **Point-in-Time Recovery (PITR):** Transaction logs are archived every 5 minutes, allowing database restoration to any second within the 7-day retention period.
- **Manual Snapshots:** Can be triggered on-demand before major upgrades using the provided `backup_rds_manual.sh` script.

### 2.2 File Storage (Amazon S3)
- **Mechanism:** S3 Bucket Versioning and Replication.
- **Strategy:** All uploaded files (PDFs, HOCR) are stored in the main InvenioRDM S3 bucket.
- **Manual Backup:** A secondary manual sync to a cold-storage bucket or local environment can be triggered using the `backup_s3_manual.sh` script.

### 2.3 Search Index (Amazon OpenSearch)
- **Mechanism:** The OpenSearch cluster is entirely derived from the primary RDS database.
- **Strategy:** In the event of a catastrophic failure, the OpenSearch index does not need to be restored from a snapshot. Instead, it is rebuilt natively using the InvenioRDM CLI (`invenio index rebuild`) after the RDS database is restored.

### 2.4 Infrastructure (Terraform State)
- **Mechanism:** Terraform state files (`terraform.tfstate`).
- **Strategy:** State files define the exact architecture of the platform. They are tracked locally and should be securely backed up to a dedicated S3 state bucket or version control.

---

## 3. Stateless and Ephemeral Components (No Backup Required)

Modern cloud architecture separates stateful data from stateless compute. The following components are explicitly excluded from backups because they hold no persistent data:

- **Compute Containers (Celery Workers, Web-UI, Web-API):** Hosted on AWS ECS Fargate. If destroyed, ECS automatically pulls the latest `ghcr.io/alabarazi/turath-rdm:develop` Docker image and restarts them. 
- **Caching (Redis / ElastiCache):** Holds temporary session data and application cache. If lost, users may need to log in again, but no permanent data is lost. It boots up empty on recovery.
- **Message Queues (Amazon MQ / SQS):** Holds in-flight Celery tasks. If a task is lost during a disaster, the user simply retries the upload/action when the system recovers.

---

## 4. Recovery Procedure (The "Test Host" Methodology)

To test a recovery (or perform an actual disaster recovery), we leverage Terraform to act as our dynamic "Test Host."

### Step 1: Provision the Recovery Environment (The Test Host)
If testing recovery, initialize a new AWS workspace or use a dedicated staging VPC.
```bash
# Apply the infrastructure code to spin up a clean environment
terraform init
terraform apply -auto-approve
```

### Step 2: Restore the Database
1. Identify the target RDS Snapshot ARN (either automated or manual).
2. Restore the snapshot to a new RDS instance via the AWS Console or CLI.
3. Update the `ecs-web-ui-service.tf` and `ecs-web-api-service.tf` to point the `RDS_DB_HOST` environment variable to the newly restored database endpoint.
4. Update the AWS Secrets Manager with the correct credentials for the restored database.

*(See `scripts/feature-backup-recovery/restore_rds_guide.sh` for exact CLI commands).*

### Step 3: Connect File Storage
1. Ensure the new environment's ECS tasks have IAM permissions to read from the primary S3 bucket, OR sync the primary bucket to a new recovery bucket.
2. Update the `S3_BUCKET_NAME` environment variable in Terraform if using a cloned bucket.

### Step 4: Rebuild Search Index
Once the Web UI and API containers are running and connected to the restored DB:
1. Connect to the running `web-ui` container:
   ```bash
   aws ecs execute-command --cluster invenio-default-cluster --task <TASK_ID> --container app --interactive --command "/bin/bash"
   ```
2. Destroy the old index and rebuild from the restored database:
   ```bash
   invenio index destroy --yes-i-know
   invenio index init
   invenio rdm-records rebuild-index
   ```

### Step 5: Verify Application Integrity
- Navigate to the Application Load Balancer URL.
- Perform a search query to verify OpenSearch rebuilt correctly.
- Open a record and verify the Mirador viewer loads the PDF from S3.

## 5. RPO and RTO Objectives
- **Recovery Point Objective (RPO):** < 5 minutes (via RDS Point-in-Time Recovery).
- **Recovery Time Objective (RTO):** ~45-60 minutes (Time to provision Terraform + restore RDS snapshot + rebuild OpenSearch index).
