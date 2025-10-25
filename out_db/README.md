# Database Exports

This folder contains **PostgreSQL database dumps** and exports.

## 💾 What Goes Here

- `.sql` dump files
- `.sqlite` database files
- Database backup files
- Exported database schemas

## 🔧 Usage

### Export PostgreSQL Database

```bash
pg_dump -U postgres -d mosques > out_db/mosques_backup_$(date +%Y%m%d).sql
```

### Import Database

```bash
psql -U postgres -d mosques < out_db/mosques_backup_20251025.sql
```

## ⚠️ Git Ignore

This folder is **git-ignored**. Database files contain large binary data and should not be committed.

## 🔐 Security

Never commit database files containing:
- Production data
- Personal information
- Sensitive mosque location data intended for internal use only

Keep backups secure and local.
