import re

# Read the original dump
with open("sqlite_backup.sql", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Modify lines for SQL Server compatibility
modified_lines = []
for line in lines:
    # Remove SQLite-specific PRAGMA statements
    if line.startswith("PRAGMA foreign_keys=OFF;"):
        continue

    # Convert AUTOINCREMENT to IDENTITY(1,1)
    line = line.replace("AUTOINCREMENT", "IDENTITY(1,1)")

    # Replace TEXT with NVARCHAR(MAX)
    line = re.sub(r"TEXT", "NVARCHAR(MAX)", line)

    # Convert INTEGER PRIMARY KEY to INT PRIMARY KEY IDENTITY
    line = re.sub(r"INTEGER PRIMARY KEY", "INT PRIMARY KEY IDENTITY(1,1)", line)

    modified_lines.append(line)

# Write the modified SQL to a new file
with open("sqlite_backup_mssql.sql", "w", encoding="utf-8") as file:
    file.writelines(modified_lines)

print("✅ SQLite dump converted successfully! File: sqlite_backup_mssql.sql")
