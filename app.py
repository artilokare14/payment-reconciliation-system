import streamlit as st
import csv
from datetime import datetime

st.title("Payment Reconciliation System")

# Load data
def load_data():
    transactions = {}
    with open("transactions.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions[row["transaction_id"]] = row

    settlements = {}
    duplicates = set()

    with open("settlements.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            txn_id = row["transaction_id"]
            if txn_id in settlements:
                duplicates.add(txn_id)
            settlements[txn_id] = row

    return transactions, settlements, duplicates


def generate_report():
    transactions, settlements, duplicates = load_data()
    report = []

    for txn_id in transactions:
        if txn_id not in settlements:
            report.append([txn_id, "Missing Settlement"])

    for txn_id in settlements:
        if txn_id not in transactions:
            report.append([txn_id, "Extra Settlement"])

    for txn_id in duplicates:
        report.append([txn_id, "Duplicate Entry"])

    for txn_id in transactions:
        if txn_id in settlements:
            amt1 = float(transactions[txn_id]["amount"])
            amt2 = float(settlements[txn_id]["amount"])
            if abs(amt1 - amt2) > 0.01:
                report.append([txn_id, "Amount Mismatch"])

    for txn_id in transactions:
        if txn_id in settlements:
            d1 = datetime.strptime(transactions[txn_id]["date"], "%Y-%m-%d")
            d2 = datetime.strptime(settlements[txn_id]["date"], "%Y-%m-%d")
            if d1.month != d2.month:
                report.append([txn_id, "Late Settlement"])

    for txn_id in settlements:
        if settlements[txn_id]["type"] == "refund" and txn_id not in transactions:
            report.append([txn_id, "Refund Error"])

    return report


if st.button("Run Reconciliation"):
    report = generate_report()

    st.write("### Results")
    st.table(report)