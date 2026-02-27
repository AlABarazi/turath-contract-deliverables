# P2-3.1: User Roles & Permissions

**Deliverable**: Implement and document user roles and permissions system for Turath InvenioRDM  
**Status**: ✅ Infrastructure Complete | ⏸️ Final Assignment Blocked by Infrastructure Issue  
**Date**: February 27, 2026  
**Production URL**: https://invenio.turath-project.com

---

## Deliverable Summary

### ✅ Completed Components

1. **Role Infrastructure** (Production Database)
   - ✅ Admin role created
   - ✅ Curator role created
   - ✅ Permissions configured (`superuser-access`, `administration-access`)

2. **User Registration**
   - ✅ `admin@turath.com` registered via website
   - ✅ Ready for role assignment

3. **Production Scripts**
   - ✅ `setup_production_roles.py` - Role creation and verification
   - ✅ `create_curator_user.py` - Curator user creation

4. **Documentation**
   - ✅ Complete implementation guide (`P2-3.1_user_roles_permissions.md`)
   - ✅ Proof documentation structure (`P2-3.1_proof/README.md`)

### ⏸️ Pending (Infrastructure Blocker)

**Issue**: Database password authentication for CLI commands  
**Root Cause**: ECS task definition missing `RDS_SECRET_ARN` environment variable  
**Impact**: Cannot execute `invenio roles add` command to assign admin role  
**Note**: This is a known recurring infrastructure issue (documented in memory: ~15 previous occurrences)

**What Works**: 
- ✅ Website database connections work perfectly
- ✅ All role infrastructure exists in database
- ✅ User registration works

**What's Blocked**:
- ❌ CLI commands for role assignment (1 SQL INSERT remaining)

---

## Files in This Deliverable

```
P2-3.1-User-Roles-Permissions/
├── README.md                          # This file
├── P2-3.1_user_roles_permissions.md   # Main documentation
├── setup_production_roles.py          # Production role setup script
├── create_curator_user.py             # Curator creation script
└── P2-3.1_proof/                      # Proof documentation
    └── README.md                      # Proof collection guide
```

---

## Current State

### Production Database (Verified)

**Roles**:
```sql
SELECT name FROM accounts_role;
-- Result: admin, curator
```

**Permissions**:
```sql
SELECT action_roles.action_id, roles.name 
FROM action_roles 
JOIN accounts_role roles ON action_roles.role_id = roles.id;
-- Result: 
-- superuser-access → admin
-- administration-access → admin
-- administration-access → curator
```

**Users**:
```sql
SELECT email FROM accounts_user WHERE email = 'admin@turath.com';
-- Result: admin@turath.com
```

**Role Assignments**: 
- Pending final assignment due to infrastructure issue

---

## Infrastructure Issue Details

### Problem
CLI commands in ECS containers cannot connect to RDS database:
```
psycopg2.OperationalError: password authentication failed for user "inveniordm_user"
```

### Attempted Solutions
1. ✅ Service restarts (multiple attempts)
2. ✅ Terraform task definition recreation
3. ✅ Force deployment with new revision
4. ❌ Result: `RDS_SECRET_ARN` still missing from deployed task definition

### Root Cause
The Terraform configuration includes the correct code:
```hcl
environment = [
  {
    name  = "RDS_SECRET_ARN"
    value = module.rds.db_instance_master_user_secret_arn
  }
]
```

But the value doesn't propagate to deployed task definitions, even after:
- Tainting and recreating task definition
- Force redeployment
- Multiple service restarts

This requires deeper investigation of the Terraform RDS module and ECS deployment pipeline.

---

## Next Steps (Post-Infrastructure Fix)

Once the infrastructure issue is resolved:

```bash
# Inside ECS container
cd /opt/invenio/var/instance
pipenv run invenio roles add admin@turath.com admin

# Verify
pipenv run invenio shell -c "from invenio_db import db; \
  result = db.session.execute(db.text('SELECT r.name FROM accounts_role r \
  JOIN accounts_userrole ur ON r.id=ur.role_id \
  JOIN accounts_user u ON ur.user_id=u.id \
  WHERE u.email=\"admin@turath.com\"')).fetchall(); \
  print([r[0] for r in result])"
```

Expected output: `['admin']`

---

## Verification Commands

### Check Website Access
```bash
curl -k -I https://invenio.turath-project.com/
# Expected: HTTP/2 200
```

### Check Admin Panel (After Assignment)
```bash
curl -k -I https://invenio.turath-project.com/administration
# Expected: HTTP/2 200 (currently 403 - role not assigned)
```

---

## Technical Notes

- **Production-Safe**: All scripts use transactions and idempotent operations
- **No Downtime**: Role infrastructure created without service interruption
- **Reversible**: All changes can be rolled back via SQL
- **Documented**: Complete error handling and verification steps included

---

## References

- Main Documentation: `P2-3.1_user_roles_permissions.md`
- Proof Collection: `P2-3.1_proof/README.md`
- Infrastructure Repo: `inveniordm-terraform` (ECS task definition issue)
- Application Repo: `turath-rdm` (scripts and documentation)
