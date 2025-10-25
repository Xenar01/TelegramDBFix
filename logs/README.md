# Log Files

This folder contains **application logs and debugging output**.

## 📝 What Goes Here

- ETL pipeline logs
- Error logs
- Debug output
- Processing summaries
- Timestamp-based log files

## 📊 Example Logs

```
logs/
├── parse_20251025_103045.log      ← ETL run logs
├── errors_20251025.log             ← Error tracking
└── import_postgres_20251025.log    ← Database import logs
```

## ⚠️ Git Ignore

This folder is **git-ignored**. Log files are ephemeral and regenerated on each run.

## 🔍 Debugging

Check logs if:
- Parser encounters errors
- Database import fails
- Data quality issues arise
- Unexpected message patterns detected

## 🧹 Maintenance

Periodically clean old logs:

```bash
# Delete logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
```

Or keep only recent logs:

```bash
# Keep last 10 log files
ls -t logs/*.log | tail -n +11 | xargs rm -f
```

## 💡 Best Practices

- Review logs after each ETL run
- Archive important logs before cleanup
- Check error logs when data looks incomplete
- Use logs to improve parser logic

See [README.md](../README.md) for troubleshooting guides.
