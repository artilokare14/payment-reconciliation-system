import csv
from datetime import datetime

# Load transactions
transactions = {}
with open("transactions.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        transactions[row["transaction_id"]] = row

# Load settlements
settlements = {}
duplicates = set()

with open("settlements.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        txn_id = row["transaction_id"]
        if txn_id in settlements:
            duplicates.add(txn_id)
        settlements[txn_id] = row

# Prepare report
report = []

# 1. Missing settlements
for txn_id in transactions:
    if txn_id not in settlements:
        report.append([txn_id, "Missing Settlement", "Not found in bank data"])

# 2. Extra settlements
for txn_id in settlements:
    if txn_id not in transactions:
        report.append([txn_id, "Extra Settlement", "Exists in bank but not in platform"])

# 3. Duplicate entries
for txn_id in duplicates:
    report.append([txn_id, "Duplicate Entry", "Appears multiple times in bank data"])

# 4. Amount mismatch (with tolerance)
for txn_id in transactions:
    if txn_id in settlements:
        amt1 = float(transactions[txn_id]["amount"])
        amt2 = float(settlements[txn_id]["amount"])
        if abs(amt1 - amt2) > 0.01:   # improved rounding logic
            report.append([txn_id, "Amount Mismatch", f"{amt1} vs {amt2}"])

# 5. Late settlement
for txn_id in transactions:
    if txn_id in settlements:
        d1 = datetime.strptime(transactions[txn_id]["date"], "%Y-%m-%d")
        d2 = datetime.strptime(settlements[txn_id]["date"], "%Y-%m-%d")
        if d1.month != d2.month:
            report.append([txn_id, "Late Settlement", f"Settled on {d2.date()}"])

# 6. Refund without original
for txn_id in settlements:
    if settlements[txn_id]["type"] == "refund" and txn_id not in transactions:
        report.append([txn_id, "Refund Error", "No original transaction"])

# 7. Remove duplicate rows (NEW IMPROVEMENT)
unique_report = []
seen = set()

for row in report:
    if tuple(row) not in seen:
        seen.add(tuple(row))
        unique_report.append(row)

report = unique_report

# 8. Save report
with open("report.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Transaction ID", "Issue Type", "Explanation"])
    writer.writerows(report)

# 9. Print output
print("\n=== Reconciliation Report ===")
for row in report:
    print(row)

# 10. Summary (BONUS - makes project look advanced 🔥)
summary = {}
for row in report:
    issue = row[1]
    summary[issue] = summary.get(issue, 0) + 1

print("\n=== Summary ===")
for k, v in summary.items():
    print(f"{k}: {v}")

print("\nReport saved as report.csv")