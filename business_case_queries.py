import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("phonepe.db")

print("=" * 60)
print("  PHONEPE TRANSACTION INSIGHTS — BUSINESS CASE STUDIES")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
# CASE 1: DECODING TRANSACTION DYNAMICS ON PHONEPE
# ══════════════════════════════════════════════════════════════
print("\nCASE 1: DECODING TRANSACTION DYNAMICS ON PHONEPE")
print("-" * 60)

# Q1.1 — Total transactions and amount by payment type
q1_1 = """
    SELECT 
        transaction_type,
        SUM(transaction_count) AS total_transactions,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM aggregated_transaction
    GROUP BY transaction_type
    ORDER BY total_transactions DESC;
"""
df1_1 = pd.read_sql_query(q1_1, conn)
print("\n🔹 Q1.1 — Total Transactions by Payment Type:")
print(df1_1.to_string(index=False))

# Q1.2 — Quarterly transaction trends (all years)
q1_2 = """
    SELECT 
        year,
        quarter,
        SUM(transaction_count) AS total_transactions,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM aggregated_transaction
    GROUP BY year, quarter
    ORDER BY year, quarter;
"""
df1_2 = pd.read_sql_query(q1_2, conn)
print("\n🔹 Q1.2 — Quarterly Transaction Trends:")
print(df1_2.to_string(index=False))

# Q1.3 — Top 10 states by total transaction amount
q1_3 = """
    SELECT 
        state,
        SUM(transaction_count) AS total_transactions,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM aggregated_transaction
    GROUP BY state
    ORDER BY total_amount DESC
    LIMIT 10;
"""
df1_3 = pd.read_sql_query(q1_3, conn)
print("\n🔹 Q1.3 — Top 10 States by Transaction Amount:")
print(df1_3.to_string(index=False))

# Q1.4 — Average transaction value by payment type
q1_4 = """
    SELECT 
        transaction_type,
        ROUND(SUM(transaction_amount) / SUM(transaction_count), 2) AS avg_transaction_value
    FROM aggregated_transaction
    GROUP BY transaction_type
    ORDER BY avg_transaction_value DESC;
"""
df1_4 = pd.read_sql_query(q1_4, conn)
print("\n🔹 Q1.4 — Average Transaction Value by Payment Type:")
print(df1_4.to_string(index=False))


# ══════════════════════════════════════════════════════════════
# CASE 4: TRANSACTION ANALYSIS FOR MARKET EXPANSION
# ══════════════════════════════════════════════════════════════
print("\n\nCASE 4: TRANSACTION ANALYSIS FOR MARKET EXPANSION")
print("-" * 60)

# Q4.1 — Year-over-year transaction growth by state
q4_1 = """
    SELECT 
        state,
        year,
        SUM(transaction_count) AS total_transactions,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM aggregated_transaction
    GROUP BY state, year
    ORDER BY state, year;
"""
df4_1 = pd.read_sql_query(q4_1, conn)
print("\n🔹 Q4.1 — Year-over-Year Transactions by State:")
print(df4_1.to_string(index=False))

# Q4.2 — States with highest transaction growth (2018 vs latest year)
q4_2 = """
    SELECT 
        a.state,
        a.total_old,
        b.total_new,
        ROUND((b.total_new - a.total_old) * 100.0 / a.total_old, 2) AS growth_pct
    FROM (
        SELECT state, SUM(transaction_count) AS total_old
        FROM aggregated_transaction WHERE year = 2018
        GROUP BY state
    ) a
    JOIN (
        SELECT state, SUM(transaction_count) AS total_new
        FROM aggregated_transaction WHERE year = 2024
        GROUP BY state
    ) b ON a.state = b.state
    ORDER BY growth_pct DESC
    LIMIT 10;
"""
df4_2 = pd.read_sql_query(q4_2, conn)
print("\n🔹 Q4.2 — Top 10 States by Transaction Growth (2018 → 2024):")
print(df4_2.to_string(index=False))

# Q4.3 — Bottom 5 states (low transactions = expansion opportunities)
q4_3 = """
    SELECT 
        state,
        SUM(transaction_count) AS total_transactions,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM aggregated_transaction
    GROUP BY state
    ORDER BY total_transactions ASC
    LIMIT 5;
"""
df4_3 = pd.read_sql_query(q4_3, conn)
print("\n🔹 Q4.3 — Bottom 5 States (Market Expansion Opportunities):")
print(df4_3.to_string(index=False))

# Q4.4 — Most popular transaction type per state
q4_4 = """
    SELECT 
        state,
        transaction_type,
        SUM(transaction_count) AS total_transactions
    FROM aggregated_transaction
    GROUP BY state, transaction_type
    HAVING SUM(transaction_count) = (
        SELECT MAX(sub.max_count)
        FROM (
            SELECT state AS s, MAX(transaction_count) AS max_count
            FROM aggregated_transaction
            WHERE state = aggregated_transaction.state
            GROUP BY state
        ) sub
    )
    ORDER BY state;
"""
# Simpler version of most popular transaction type per state
q4_4_simple = """
    SELECT 
        state,
        transaction_type,
        SUM(transaction_count) AS total_count
    FROM aggregated_transaction
    GROUP BY state, transaction_type
    ORDER BY state, total_count DESC;
"""
df4_4 = pd.read_sql_query(q4_4_simple, conn)
# Get top type per state
df4_4 = df4_4.groupby("state").first().reset_index()
print("\n🔹 Q4.4 — Most Popular Transaction Type per State:")
print(df4_4.to_string(index=False))


# ══════════════════════════════════════════════════════════════
# CASE 5: USER ENGAGEMENT AND GROWTH STRATEGY
# ══════════════════════════════════════════════════════════════
print("\n\nCASE 5: USER ENGAGEMENT AND GROWTH STRATEGY")
print("-" * 60)

# Q5.1 — Total registered users and app opens by state
q5_1 = """
    SELECT 
        state,
        SUM(registered_users) AS total_registered_users,
        SUM(app_opens) AS total_app_opens
    FROM aggregated_user
    GROUP BY state
    ORDER BY total_registered_users DESC;
"""
df5_1 = pd.read_sql_query(q5_1, conn)
print("\n🔹 Q5.1 — Registered Users & App Opens by State:")
print(df5_1.to_string(index=False))

# Q5.2 — User engagement rate (app opens per registered user)
q5_2 = """
    SELECT 
        state,
        SUM(registered_users) AS total_users,
        SUM(app_opens) AS total_app_opens,
        ROUND(CAST(SUM(app_opens) AS FLOAT) / NULLIF(SUM(registered_users), 0), 2) AS engagement_rate
    FROM aggregated_user
    GROUP BY state
    ORDER BY engagement_rate DESC
    LIMIT 10;
"""
df5_2 = pd.read_sql_query(q5_2, conn)
print("\n🔹 Q5.2 — Top 10 States by User Engagement Rate (App Opens/User):")
print(df5_2.to_string(index=False))

# Q5.3 — Year-wise user growth across India
q5_3 = """
    SELECT 
        year,
        SUM(registered_users) AS total_registered_users,
        SUM(app_opens) AS total_app_opens
    FROM aggregated_user
    GROUP BY year
    ORDER BY year;
"""
df5_3 = pd.read_sql_query(q5_3, conn)
print("\n🔹 Q5.3 — Year-wise User Growth Across India:")
print(df5_3.to_string(index=False))

# Q5.4 — Top 10 districts by registered users
q5_4 = """
    SELECT 
        state,
        district,
        SUM(registered_users) AS total_users,
        SUM(app_opens) AS total_app_opens
    FROM map_user
    GROUP BY state, district
    ORDER BY total_users DESC
    LIMIT 10;
"""
df5_4 = pd.read_sql_query(q5_4, conn)
print("\n🔹 Q5.4 — Top 10 Districts by Registered Users:")
print(df5_4.to_string(index=False))


# ══════════════════════════════════════════════════════════════
# CASE 7: TRANSACTION ANALYSIS ACROSS STATES AND DISTRICTS
# ══════════════════════════════════════════════════════════════
print("\n\nCASE 7: TRANSACTION ANALYSIS ACROSS STATES AND DISTRICTS")
print("-" * 60)

# Q7.1 — Top 10 states by transaction count
q7_1 = """
    SELECT 
        state,
        SUM(transaction_count) AS total_count,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM top_transaction
    WHERE entity_type = 'district'
    GROUP BY state
    ORDER BY total_count DESC
    LIMIT 10;
"""
df7_1 = pd.read_sql_query(q7_1, conn)
print("\n🔹 Q7.1 — Top 10 States by Transaction Count:")
print(df7_1.to_string(index=False))

# Q7.2 — Top 10 districts by transaction amount
q7_2 = """
    SELECT 
        state,
        entity_name AS district,
        SUM(transaction_count) AS total_count,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM top_transaction
    WHERE entity_type = 'district'
    GROUP BY state, entity_name
    ORDER BY total_amount DESC
    LIMIT 10;
"""
df7_2 = pd.read_sql_query(q7_2, conn)
print("\n🔹 Q7.2 — Top 10 Districts by Transaction Amount:")
print(df7_2.to_string(index=False))

# Q7.3 — Top 10 pincodes by transaction count
q7_3 = """
    SELECT 
        state,
        entity_name AS pincode,
        SUM(transaction_count) AS total_count,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM top_transaction
    WHERE entity_type = 'pincode'
    GROUP BY state, entity_name
    ORDER BY total_count DESC
    LIMIT 10;
"""
df7_3 = pd.read_sql_query(q7_3, conn)
print("\n🔹 Q7.3 — Top 10 Pincodes by Transaction Count:")
print(df7_3.to_string(index=False))

# Q7.4 — Quarter with highest transactions overall
q7_4 = """
    SELECT 
        year,
        quarter,
        SUM(transaction_count) AS total_count,
        ROUND(SUM(transaction_amount), 2) AS total_amount
    FROM top_transaction
    GROUP BY year, quarter
    ORDER BY total_count DESC
    LIMIT 5;
"""
df7_4 = pd.read_sql_query(q7_4, conn)
print("\n🔹 Q7.4 — Top 5 Year-Quarter Combinations by Transactions:")
print(df7_4.to_string(index=False))


# ══════════════════════════════════════════════════════════════
# CASE 8: USER REGISTRATION ANALYSIS
# ══════════════════════════════════════════════════════════════
print("\n\nCASE 8: USER REGISTRATION ANALYSIS")
print("-" * 60)

# Q8.1 — Top 10 states by registered users
q8_1 = """
    SELECT 
        state,
        SUM(registered_users) AS total_registered_users
    FROM top_user
    WHERE entity_type = 'district'
    GROUP BY state
    ORDER BY total_registered_users DESC
    LIMIT 10;
"""
df8_1 = pd.read_sql_query(q8_1, conn)
print("\n🔹 Q8.1 — Top 10 States by Registered Users:")
print(df8_1.to_string(index=False))

# Q8.2 — Top 10 districts by registered users
q8_2 = """
    SELECT 
        state,
        entity_name AS district,
        SUM(registered_users) AS total_registered_users
    FROM top_user
    WHERE entity_type = 'district'
    GROUP BY state, entity_name
    ORDER BY total_registered_users DESC
    LIMIT 10;
"""
df8_2 = pd.read_sql_query(q8_2, conn)
print("\n🔹 Q8.2 — Top 10 Districts by Registered Users:")
print(df8_2.to_string(index=False))

# Q8.3 — Top 10 pincodes by registered users
q8_3 = """
    SELECT 
        state,
        entity_name AS pincode,
        SUM(registered_users) AS total_registered_users
    FROM top_user
    WHERE entity_type = 'pincode'
    GROUP BY state, entity_name
    ORDER BY total_registered_users DESC
    LIMIT 10;
"""
df8_3 = pd.read_sql_query(q8_3, conn)
print("\n🔹 Q8.3 — Top 10 Pincodes by Registered Users:")
print(df8_3.to_string(index=False))

# Q8.4 — Quarter with highest new user registrations
q8_4 = """
    SELECT 
        year,
        quarter,
        SUM(registered_users) AS total_registered_users
    FROM top_user
    GROUP BY year, quarter
    ORDER BY total_registered_users DESC
    LIMIT 5;
"""
df8_4 = pd.read_sql_query(q8_4, conn)
print("\n🔹 Q8.4 — Top 5 Year-Quarter Combinations by User Registrations:")
print(df8_4.to_string(index=False))


# ══════════════════════════════════════════════════════════════
conn.close()
print("\n\n All business case queries executed successfully!")
print("=" * 60)
