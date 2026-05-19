from datetime import datetime, timedelta
import pandas as pd


def run_attribution_pipeline(
    dms_file_path, ip_log_path, date_range_days=90, output_path="attribution_report.csv"
):
    """Executes the closed-loop attribution algorithm matching DMS sales data

    with publisher IP logs using household addresses.
    """
    print("--- Step 1: Onboarding & Filtering DMS Data ---")
    # Load raw DMS first-party data
    # Expected columns: 'sold_date', 'vin', 'customer_name', 'phone', 'address', 'sale_amount', 'model'
    dms_df = pd.read_csv(dms_file_path)

    # Ensure date column is a datetime object
    dms_df["sold_date"] = pd.to_datetime(dms_df["sold_date"])

    # Filter based on the requested date range (30, 60, or 90 days)
    cutoff_date = datetime.now() - timedelta(days=date_range_days)
    sales_in_range = dms_df[dms_df["sold_date"] >= cutoff_date].copy()
    print(
        f"Found {len(sales_in_range)} sales within the last {date_range_days} days."
    )

    print("\n--- Step 2: Anonymizing Data (Stripping PII except Address) ---")
    # Store the full sales information separately for the final re-join step.
    # We use 'vin' as our immutable unique identifier.
    full_sales_data = sales_in_range.copy()

    # Create a stripped identity matching dataframe (only VIN and Address)
    # This ensures no names, emails, or phones are used during the matching lookup
    identity_lookup_df = sales_in_range[["vin", "address"]].copy()

    print(
        "\n--- Step 3: Onboarding Aggregator IP Log File & Identity Map ---")
    # Load publisher/aggregator logs
    # Expected columns: 'ip_address', 'address' (from a household identity graph like LiveRamp, Neustar, etc.)
    ip_log_df = pd.read_csv(ip_log_path)

    print("\n--- Step 4 & 5: Matching Addresses & Resolving Node Density ---")
    # Merge the stripped DMS data with the IP logs based on the household address.
    # Because VINs are completely unique, any duplication from dense physical nodes
    # resolves itself when we map back to the unique vehicle sale.
    matched_identities = pd.merge(
        identity_lookup_df, ip_log_df, on="address", how="inner"
    )

    # Flag these matches as verified attribution
    matched_identities["attribution_match"] = "Yes"

    # Deduplicate by VIN to ensure one unique vehicle sale doesn't claim multiple duplicate attributions
    matched_identities = matched_identities.drop_duplicates(subset=["vin"])

    print(
        f"Successfully matched {len(matched_identities)} households to digital IP footprints."
    )

    print("\n--- Step 6: Reconnecting Matches to Full Sales Data & Exporting ---")
    # Connect the verified matches back to the rich DMS sales data using the unique VIN
    final_attribution_report = pd.merge(
        full_sales_data,
        matched_identities[["vin", "ip_address", "attribution_match"]],
        on="vin",
        how="left",
    )

    # Fill non-matches with 'No'
    final_attribution_report["attribution_match"] = final_attribution_report[
        "attribution_match"
    ].fillna("No")

    # Filter to only export the successful attributions
    successful_matches = final_attribution_report[
        final_attribution_report["attribution_match"] == "Yes"
    ]

    # Export to CSV
    successful_matches.to_csv(output_path, index=False)
    print(f"Success! Attribution report exported to: {output_path}")

    return successful_matches


# ==========================================
# EXAMPLE EXECUTION (How to use the script)
# ==========================================
if __name__ == "__main__":
    # This section creates dummy data files just so you can run this script out-of-the-box to test it.

    # 1. Create Mock DMS Data
    mock_dms = pd.DataFrame(
        {
            "sold_date": [
                (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d"),
            ],  # Out of range
            "vin": ["VIN123456789ONE", "VIN987654321TWO", "VIN555555555THREE"],
            "customer_name": ["John Doe", "Jane Smith", "Bob Johnson"],
            "address": [
                "123 Main St, Dallas TX",
                "456 Oak Ave, Austin TX",
                "789 Pine Rd, Houston TX",
            ],
            "gross_profit": [3500, 4200, 2800],
        }
    )
    mock_dms.to_csv("mock_dms.csv", index=False)

    # 2. Create Mock Aggregator IP Log (Mapping residential IPs to Household Addresses)
    mock_publisher_ips = pd.DataFrame(
        {
            "ip_address": ["192.168.1.50", "172.16.254.1"],
            "address": [
                "123 Main St, Dallas TX",
                "999 Fake St, Nowhere TX",
            ],  # 123 Main matches, 456 Oak didn't visit site
        }
    )
    mock_publisher_ips.to_csv("mock_ip_logs.csv", index=False)

    # 3. Run the pipeline for a 60-day report
    report = run_attribution_pipeline(
        dms_file_path="mock_dms.csv",
        ip_log_path="mock_ip_logs.csv",
        date_range_days=60,
        output_path="dealer_attribution_results.csv",
    )
