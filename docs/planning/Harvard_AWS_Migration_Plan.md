# Migration Plan: Turath InvenioRDM to Harvard AWS

**Date:** October 26, 2025
**Subject:** Documenting steps, considerations, and estimated effort for migrating the Turath InvenioRDM environment to Harvard's AWS infrastructure.

## Executive Summary
The Turath InvenioRDM instance is currently deployed on a private AWS environment using an Infrastructure-as-Code (IaC) approach via Terraform. Migrating to Harvard's AWS infrastructure will primarily involve re-running these Terraform scripts in the new environment, migrating the data volumes (RDS and EFS), and updating DNS records. 

Because the architecture is fully containerized (ECS/Fargate) and codified, the migration effort is highly predictable and low-risk.

## Target Architecture (Harvard AWS)
The target architecture must mirror our current setup to ensure compatibility:
- **VPC:** 2 Public Subnets, 2 Private Subnets, NAT Gateways
- **Compute:** ECS Fargate (Web UI, Web API, Celery Workers, Search Microservice, Cantaloupe)
- **Database:** Amazon RDS PostgreSQL 13+
- **Search:** Amazon OpenSearch Service (or self-hosted ELK in ECS if mandated by Harvard policies)
- **Cache/MQ:** Amazon ElastiCache (Redis) and Amazon MQ (RabbitMQ)
- **Storage:** Amazon EFS (Shared persistent storage for HOCR, Cantaloupe derivative cache, and system files)
- **Routing:** Application Load Balancer (ALB) with AWS Certificate Manager (ACM) for SSL

## Migration Phases & Runbook

### Phase 1: Preparation & Access (Estimated Effort: 1-2 Days)
Before touching any code, the following administrative prerequisites must be met by Harvard IT:
1. **AWS Account Access:** Provision an IAM User or Role with permissions to manage VPC, ECS, RDS, EFS, ElastiCache, ALBs, and Route53.
2. **Terraform State Backend:** Create an S3 bucket in the Harvard account to store the remote Terraform state.
3. **Domain & SSL:** Provide the target domain name (e.g., `invenio.fas.harvard.edu`) and generate an SSL certificate in AWS ACM in the target region.
4. **Environment Variables Check:** Review the `terraform.tfvars.json` and `secrets.yml` files. Update the domain names, region, and generate new passwords/secrets for the Harvard environment.

### Phase 2: Infrastructure Provisioning (Estimated Effort: 1 Day)
Because the infrastructure is codified in the `inveniordm-terraform` repository, provisioning the new environment is highly automated.
1. Update `0-main.tf` to point to the new Harvard S3 backend for state management.
2. Initialize Terraform: `terraform init`
3. Review the execution plan: `terraform plan -var-file="terraform.tfvars.json"`
4. Apply the infrastructure: `terraform apply`
   *Note: This will spin up the VPC, RDS, OpenSearch, EFS, and ECS Clusters. It will take approximately 30-45 minutes.*

### Phase 3: Application Deployment (Estimated Effort: 1 Day)
1. **GitHub Actions / ECR:** Update the CI/CD pipeline (if migrating to a new GitHub repo) or simply point the existing GitHub Actions to push Docker images to the Harvard AWS Elastic Container Registry (ECR).
2. **Deploy Images:** Once the images (`turath-rdm:develop` and `turath-search-service:develop`) are in the Harvard ECR, Terraform will pull them to start the ECS Fargate tasks.
3. **Database Initialization:** Run the initial setup scripts on the new database:
   ```bash
   invenio db init
   invenio db create
   invenio index init
   ```

### Phase 4: Data Migration (Estimated Effort: 2-4 Days, depending on data size)
This is the most critical phase. We must migrate the relational database and the persistent files.
1. **RDS Migration:**
   - Create a pg_dump from the existing production RDS instance.
   - Restore the dump to the new Harvard RDS instance.
2. **EFS File Migration:**
   - The EFS volume holds the uploaded PDFs, HOCR files, and Cantaloupe caches.
   - Use AWS DataSync to securely and efficiently transfer data from the old EFS volume to the new Harvard EFS volume.
3. **OpenSearch Reindexing:**
   - Instead of migrating the OpenSearch indices directly, it is cleaner to rebuild them from the migrated database.
   - Connect to a web-ui or worker container and run: `invenio rdm-records rebuild-all-indices`

### Phase 5: Cutover & Validation (Estimated Effort: 1 Day)
1. **DNS Cutover:** Update the Route53 alias records to point the production domain to the new Harvard ALB.
2. **Validation Testing:** Run the automated search robustness tests (`scripts/run_search_tests.py`) against the new domain.
3. **UI/UX Testing:** Manually verify that IIIF manifests load correctly, Mirador renders the PDFs, and the text overlay works as expected.

## Total Estimated Effort
**~1 to 2 Weeks (assuming prompt access provisioning by Harvard IT).** 
The actual technical execution time is less than 3 days, but coordination, security reviews, and large data transfers usually extend the timeline.

## Risk Factors to Discuss with Harvard IT
1. **OpenSearch Hosting:** Does Harvard prefer managed Amazon OpenSearch, or do they require us to host ELK directly on EC2/ECS for cost reasons?
2. **EFS Costs:** Turath relies heavily on EFS for shared filesystem access between Cantaloupe and the Invenio containers. Ensure Harvard is aware of EFS pricing models (Standard vs. One Zone).
3. **VPC Peering:** Will the InvenioRDM instance need to talk to other internal Harvard systems? If so, VPC peering configuration must be added to the Terraform scripts.
