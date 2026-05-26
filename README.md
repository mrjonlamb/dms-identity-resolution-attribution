# dms-identity-resolution-attribution
An identity resolution and closed-loop attribution algorithm for automotive retail. Programmatically bridges de-identified DMS sales data with digital publisher IP logs using household matching and immutable VIN verification to solve the walk-in attribution blind spot safely and securely.

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/fe5d1f75-26bd-4a43-bd6f-7e999bf5130f" />


# Closed-Loop Automotive Attribution via De-Identified DMS & Edge IP Resolution

## 🏎️ The Problem in Automotive Retail
Modern automotive digital publishers and aggregators (e.g., CarGurus, Autotrader, Cars.com) struggle to definitively prove their Return on Ad Spend (ROAS). Typical digital attribution relies heavily on third-party cookies or form-fills (leads). However, **over 80% of dealership walk-ins buy a car without ever submitting a digital lead form.** Because of this "blind spot," publishers cannot accurately claim credit for the offline vehicle sales they drove, and dealers struggle to know which digital marketing channels actually generate gross profit.

## 💡 The Solution
This repository contains the core programmatic logic for a privacy-first, closed-loop attribution algorithm. 

Instead of relying on fragile digital tracking links or intrusive PII (Personally Identifiable Information) sharing, this system utilizes a **household-level identity resolution methodology** that safely connects offline dealership sales directly to digital publisher footprints.

### 🔄 The Algorithm Workflow

1. **DMS Data Onboarding & Temporal Filtering:** First-party sales data is ingested from the Dealership Management System (DMS) and dynamically filtered based on a targeted lookback window (30, 60, or 90 days).
2. **PII Striping & Anonymization:** To ensure absolute consumer privacy and compliance, all direct PII (Names, Phones, Emails) is stripped out. The algorithm isolates *only* the physical delivery address linked to a unique vehicle identifier (VIN).
3. **Publisher Log Ingestion:** Digital footprint logs (IP addresses mapped to physical households via a compliant residential identity graph) are ingested from the publisher/aggregator site.
4. **Deterministic Identity Matching:** The algorithm performs a deterministic join between the de-identified DMS addresses and the publisher IP logs.
5. **High-Density Node Resolution:** In high-density living areas (e.g., apartment complexes or shared neighborhood ISP nodes) where multiple households share an IP footprint, the algorithm leverages the **immutability of the VIN**. Because a physical vehicle can only be sold to one household at a time, the unique VIN prevents false positives and automatically resolves the match to the true buying residence.
6. **Closed-Loop Attribution & Re-Identification:** Verified matches are appended back to the rich DMS operational data (e.g., gross profit, vehicle make/model), giving the dealer an exact dollar-for-dollar ROI report.

---

## 💻 Getting Started (Python Implementation)

The Python script included in this repository provides a fully functional, modular pipeline using `pandas` to demonstrate the data engineering mechanics of the patent logic.

### Prerequisites
```bash
pip install pandas

