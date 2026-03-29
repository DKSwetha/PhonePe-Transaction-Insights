import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PhonePe Transaction Insights",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM STYLE
# ─────────────────────────────────────────────
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; }
        h1, h2, h3 { color: #a78bde; }
        div[data-testid="metric-container"] {
            background-color: #2d2d2d;
            border: 1px solid #5f259f;
            border-radius: 10px;
            padding: 10px;
        }
        div[data-testid="metric-container"] label {
            color: #a78bde !important;
        }
        div[data-testid="metric-container"] div {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────
@st.cache_data
def load_table(query):
    conn = sqlite3.connect("phonepe.db")
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load all tables once
@st.cache_data
def load_all():
    conn = sqlite3.connect("phonepe.db")
    agg_txn  = pd.read_sql("SELECT * FROM aggregated_transaction", conn)
    agg_user = pd.read_sql("SELECT * FROM aggregated_user", conn)
    agg_ins  = pd.read_sql("SELECT * FROM aggregated_insurance", conn)
    map_txn  = pd.read_sql("SELECT * FROM map_transaction", conn)
    map_user = pd.read_sql("SELECT * FROM map_user", conn)
    top_txn  = pd.read_sql("SELECT * FROM top_transaction", conn)
    top_user = pd.read_sql("SELECT * FROM top_user", conn)
    conn.close()

    # Feature engineering
    agg_txn['amount_cr']  = agg_txn['transaction_amount']  / 1e7
    agg_ins['amount_cr']  = agg_ins['insurance_amount']    / 1e7
    map_txn['amount_cr']  = map_txn['transaction_amount']  / 1e7
    agg_txn['year_quarter'] = agg_txn['year'].astype(str) + ' Q' + agg_txn['quarter'].astype(str)
    agg_user['year_quarter'] = agg_user['year'].astype(str) + ' Q' + agg_user['quarter'].astype(str)
    agg_user['engagement_rate'] = (agg_user['app_opens'] /
                                   agg_user['registered_users'].replace(0, float('nan'))).round(2)
    return agg_txn, agg_user, agg_ins, map_txn, map_user, top_txn, top_user

agg_txn, agg_user, agg_ins, map_txn, map_user, top_txn, top_user = load_all()

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
st.sidebar.title("Navigation")

pages = [
    "Home — Overview",
    "Case 1: Transaction Dynamics",
    "Case 4: Market Expansion",
    "Case 5: User Engagement",
    "Case 7: Top States & Districts",
    "Case 8: User Registration",
]
page = st.sidebar.radio("Go to", pages)
st.sidebar.markdown("---")
st.sidebar.markdown("**Data:** PhonePe Pulse (2018–2024)")
st.sidebar.markdown("**Tables:** 9 | **Rows:** ~98,678")

# ══════════════════════════════════════════════
# PAGE 1: HOME OVERVIEW
# ══════════════════════════════════════════════
if page == "Home — Overview":
    st.title(" PhonePe Transaction Insights Dashboard")
    st.markdown("### An end-to-end analysis of PhonePe's transaction, user & insurance data (2018–2024)")
    st.markdown("---")

    # KPI Metrics
    total_txn   = agg_txn['transaction_count'].sum()
    total_amt   = agg_txn['transaction_amount'].sum()
    total_users = agg_user['registered_users'].sum()
    total_opens = agg_user['app_opens'].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(" Total Transactions", f"{total_txn/1e9:.1f}B")
    c2.metric(" Total Amount", f"₹{total_amt/1e12:.1f}T")
    c3.metric(" Registered Users", f"{total_users/1e9:.1f}B")
    c4.metric(" App Opens", f"{total_opens/1e9:.1f}B")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Quarterly growth line chart
        india_q = agg_txn.groupby(['year', 'quarter', 'year_quarter']).agg(
            count=('transaction_count', 'sum')
        ).reset_index().sort_values(['year', 'quarter'])
        fig = px.line(india_q, x='year_quarter', y='count',
                      title='India — Quarterly Transaction Growth',
                      labels={'count': 'Transactions', 'year_quarter': 'Quarter'},
                      color_discrete_sequence=['#5f259f'])
        fig.update_traces(mode='lines+markers', fill='tozeroy', fillcolor='rgba(95,37,159,0.1)')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Payment type pie
        type_totals = agg_txn.groupby('transaction_type')['transaction_count'].sum().reset_index()
        fig2 = px.pie(type_totals, names='transaction_type', values='transaction_count',
                      title='Transaction Count by Payment Type',
                      color_discrete_sequence=px.colors.sequential.Purples_r)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Top 10 states by transaction amount
        state_amt = agg_txn.groupby('state')['amount_cr'].sum().reset_index().sort_values('amount_cr', ascending=False).head(10)
        fig3 = px.bar(state_amt, x='amount_cr', y='state', orientation='h',
                      title=' Top 10 States by Transaction Amount (₹ Crores)',
                      labels={'amount_cr': '₹ Crores', 'state': 'State'},
                      color='amount_cr', color_continuous_scale='Purples')
        fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # User growth by year
        user_yr = agg_user.groupby('year')['registered_users'].sum().reset_index()
        fig4 = px.bar(user_yr, x='year', y='registered_users',
                      title=' Registered Users by Year',
                      labels={'registered_users': 'Registered Users', 'year': 'Year'},
                      color='registered_users', color_continuous_scale='Blues')
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════
# PAGE 2: CASE 1 — TRANSACTION DYNAMICS
# ══════════════════════════════════════════════
elif page == "Case 1: Transaction Dynamics":
    st.title("Case 1: Decoding Transaction Dynamics on PhonePe")
    st.markdown("*Understanding how payment types, states, and time periods drive transaction behavior.*")
    st.markdown("---")

    # Filters
    col_f1, col_f2 = st.columns(2)
    years = sorted(agg_txn['year'].unique())
    sel_years = col_f1.multiselect("Select Years", years, default=years)
    quarters = sorted(agg_txn['quarter'].unique())
    sel_quarters = col_f2.multiselect("Select Quarters", quarters, default=quarters)

    filtered = agg_txn[agg_txn['year'].isin(sel_years) & agg_txn['quarter'].isin(sel_quarters)]

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Transactions", f"{filtered['transaction_count'].sum()/1e9:.2f}B")
    k2.metric("Total Amount", f"₹{filtered['transaction_amount'].sum()/1e12:.2f}T")
    k3.metric("Avg Transaction Value",
              f"₹{filtered['transaction_amount'].sum()/filtered['transaction_count'].sum():,.0f}")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        # Bar: transaction count by type
        type_count = filtered.groupby('transaction_type')['transaction_count'].sum().reset_index()
        fig = px.bar(type_count.sort_values('transaction_count', ascending=False),
                     x='transaction_type', y='transaction_count',
                     title='Transaction Count by Payment Type',
                     color='transaction_type',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Pie: amount share by type
        type_amt = filtered.groupby('transaction_type')['amount_cr'].sum().reset_index()
        fig2 = px.pie(type_amt, names='transaction_type', values='amount_cr',
                      title='Transaction Amount Share by Payment Type',
                      color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Line: quarterly trend
        q_trend = filtered.groupby(['year', 'quarter', 'year_quarter'])['transaction_count'].sum().reset_index().sort_values(['year', 'quarter'])
        fig3 = px.line(q_trend, x='year_quarter', y='transaction_count',
                       title='Quarterly Transaction Count Trend',
                       markers=True, color_discrete_sequence=['#5f259f'])
        fig3.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Bar: avg transaction value by type
        type_avg = filtered.groupby('transaction_type').apply(
            lambda x: x['transaction_amount'].sum() / x['transaction_count'].sum()
        ).reset_index()
        type_avg.columns = ['transaction_type', 'avg_value']
        fig4 = px.bar(type_avg.sort_values('avg_value', ascending=False),
                      x='transaction_type', y='avg_value',
                      title='Average Transaction Value by Payment Type (₹)',
                      color='avg_value', color_continuous_scale='Purples')
        st.plotly_chart(fig4, use_container_width=True)

    # Insight box
    st.info("""
    ** Key Insights:**
    - Merchant Payments dominate in **volume** (781B transactions) but Peer-to-peer leads in **value** (avg ₹3,134 per txn)
    - Transactions grew **210x** from 2018 Q1 to 2024 Q4
    - Q4 is consistently the highest performing quarter (festive season effect)
    """)

# ══════════════════════════════════════════════
# PAGE 3: CASE 4 — MARKET EXPANSION
# ══════════════════════════════════════════════
elif page == "Case 4: Market Expansion":
    st.title(" Case 4: Transaction Analysis for Market Expansion")
    st.markdown("*Identifying high-growth states and untapped expansion opportunities.*")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # YoY growth bar (2018 vs 2024)
        old = agg_txn[agg_txn['year'] == 2018].groupby('state')['transaction_count'].sum()
        new = agg_txn[agg_txn['year'] == 2024].groupby('state')['transaction_count'].sum()
        growth = pd.DataFrame({'old': old, 'new': new}).dropna()
        growth['growth_pct'] = ((growth['new'] - growth['old']) / growth['old'] * 100).round(2)
        growth = growth.reset_index().sort_values('growth_pct', ascending=False).head(10)
        fig = px.bar(growth, x='growth_pct', y='state', orientation='h',
                     title='Top 10 States by Transaction Growth (2018 → 2024, %)',
                     color='growth_pct', color_continuous_scale='Greens',
                     labels={'growth_pct': 'Growth %', 'state': 'State'})
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bottom 5 states (expansion opportunities)
        state_total = agg_txn.groupby('state')['transaction_count'].sum().reset_index().sort_values('transaction_count').head(5)
        fig2 = px.bar(state_total, x='transaction_count', y='state', orientation='h',
                      title='Bottom 5 States — Expansion Opportunities',
                      color='transaction_count', color_continuous_scale='Oranges',
                      labels={'transaction_count': 'Transaction Count', 'state': 'State'})
        st.plotly_chart(fig2, use_container_width=True)

    # State-wise year trend
    top5_states = agg_txn.groupby('state')['transaction_count'].sum().nlargest(5).index.tolist()
    sel_states = st.multiselect("Select States to Compare", sorted(agg_txn['state'].unique()), default=top5_states)
    state_year = agg_txn[agg_txn['state'].isin(sel_states)].groupby(['state', 'year'])['transaction_count'].sum().reset_index()
    fig3 = px.line(state_year, x='year', y='transaction_count', color='state',
                   title='Year-over-Year Transaction Count by State',
                   markers=True,
                   labels={'transaction_count': 'Transaction Count', 'year': 'Year'})
    st.plotly_chart(fig3, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Most popular payment type per state
        pop_type = agg_txn.groupby(['state', 'transaction_type'])['transaction_count'].sum().reset_index()
        pop_type = pop_type.loc[pop_type.groupby('state')['transaction_count'].idxmax()]
        fig4 = px.bar(pop_type.sort_values('transaction_count', ascending=False).head(15),
                      x='state', y='transaction_count', color='transaction_type',
                      title='Most Popular Payment Type per State (Top 15)',
                      labels={'transaction_count': 'Count', 'state': 'State'})
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        # Pie: payment type dominance across India
        dom = pop_type['transaction_type'].value_counts().reset_index()
        dom.columns = ['transaction_type', 'state_count']
        fig5 = px.pie(dom, names='transaction_type', values='state_count',
                      title='Payment Type Dominance Across States',
                      color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig5, use_container_width=True)

    st.info("""
    ** Key Insights:**
    - **Andaman & Nicobar** grew 34,683% — highest growth rate from 2018 to 2024
    - **Lakshadweep, Mizoram, Ladakh** have lowest transaction volumes — biggest expansion opportunities
    - **Merchant Payments** dominate in 30 out of 36 states — confirms its universal appeal
    """)

# ══════════════════════════════════════════════
# PAGE 4: CASE 5 — USER ENGAGEMENT
# ══════════════════════════════════════════════
elif page == "Case 5: User Engagement":
    st.title(" Case 5: User Engagement and Growth Strategy")
    st.markdown("*Analyzing how actively users engage with the PhonePe app across states.*")
    st.markdown("---")

    # Filters
    sel_year = st.select_slider("Select Year", options=sorted(agg_user['year'].unique()), value=2024)
    filtered_user = agg_user[agg_user['year'] == sel_year]

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Registered Users", f"{filtered_user['registered_users'].sum()/1e9:.2f}B")
    k2.metric("App Opens", f"{filtered_user['app_opens'].sum()/1e9:.2f}B")
    k3.metric("Avg Engagement Rate",
              f"{(filtered_user['app_opens'].sum()/filtered_user['registered_users'].sum()):.1f}x")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        # Top 10 states by registered users
        state_users = filtered_user.groupby('state')['registered_users'].sum().reset_index().sort_values('registered_users', ascending=False).head(10)
        fig = px.bar(state_users, x='registered_users', y='state', orientation='h',
                     title=f'Top 10 States by Registered Users ({sel_year})',
                     color='registered_users', color_continuous_scale='Blues',
                     labels={'registered_users': 'Registered Users', 'state': 'State'})
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top 10 states by engagement rate
        eng = filtered_user.groupby('state').agg(
            users=('registered_users', 'sum'),
            opens=('app_opens', 'sum')
        ).reset_index()
        eng['rate'] = (eng['opens'] / eng['users'].replace(0, float('nan'))).round(2)
        eng = eng.sort_values('rate', ascending=False).head(10)
        fig2 = px.bar(eng, x='rate', y='state', orientation='h',
                      title=f'Top 10 States by Engagement Rate ({sel_year})',
                      color='rate', color_continuous_scale='Greens',
                      labels={'rate': 'App Opens per User', 'state': 'State'})
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Year-wise user growth
        yr_growth = agg_user.groupby('year').agg(
            users=('registered_users', 'sum'),
            opens=('app_opens', 'sum')
        ).reset_index()
        fig3 = px.line(yr_growth, x='year', y=['users', 'opens'],
                       title='Year-wise User & App Opens Growth',
                       markers=True,
                       labels={'value': 'Count', 'year': 'Year', 'variable': 'Metric'})
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Top 10 districts by registered users
        dist_users = map_user.groupby(['state', 'district'])['registered_users'].sum().reset_index().sort_values('registered_users', ascending=False).head(10)
        dist_users['label'] = dist_users['district'] + ', ' + dist_users['state']
        fig4 = px.bar(dist_users, x='registered_users', y='label', orientation='h',
                      title='Top 10 Districts by Registered Users',
                      color='registered_users', color_continuous_scale='Purples',
                      labels={'registered_users': 'Users', 'label': 'District'})
        fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig4, use_container_width=True)

    st.info("""
    ** Key Insights:**
    - **Maharashtra** leads with the most registered users consistently
    - **Meghalaya** has the highest engagement rate (174 app opens per user!) — highly active user base
    - **Delhi** has huge user base but low engagement — potential for re-engagement campaigns
    - User registrations grew **7.6x** from 2018 to 2024
    """)

# ══════════════════════════════════════════════
# PAGE 5: CASE 7 — TOP STATES & DISTRICTS
# ══════════════════════════════════════════════
elif page == "Case 7: Top States & Districts":
    st.title(" Case 7: Transaction Analysis Across States and Districts")
    st.markdown("*Identifying top-performing geographies by transaction volume and value.*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["States", "Districts", " Pincodes"])

    with tab1:
        n_states = st.slider("Number of top states to show", 5, 20, 10)
        top_states = top_txn[top_txn['entity_type'] == 'district'].groupby('state').agg(
            count=('transaction_count', 'sum'),
            amount=('transaction_amount', 'sum')
        ).reset_index().sort_values('count', ascending=False).head(n_states)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(top_states, x='count', y='state', orientation='h',
                         title=f'Top {n_states} States by Transaction Count',
                         color='count', color_continuous_scale='Purples',
                         labels={'count': 'Transaction Count', 'state': 'State'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(top_states.sort_values('amount', ascending=False),
                          x='amount', y='state', orientation='h',
                          title=f'Top {n_states} States by Transaction Amount (₹)',
                          color='amount', color_continuous_scale='Greens',
                          labels={'amount': 'Transaction Amount (₹)', 'state': 'State'})
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        n_dist = st.slider("Number of top districts to show", 5, 20, 10)
        top_dist = top_txn[top_txn['entity_type'] == 'district'].groupby(['state', 'entity_name']).agg(
            count=('transaction_count', 'sum'),
            amount=('transaction_amount', 'sum')
        ).reset_index().sort_values('amount', ascending=False).head(n_dist)
        top_dist['label'] = top_dist['entity_name'] + ', ' + top_dist['state']

        fig3 = px.bar(top_dist, x='amount', y='label', orientation='h',
                      title=f'Top {n_dist} Districts by Transaction Amount (₹)',
                      color='amount', color_continuous_scale='Blues',
                      labels={'amount': '₹ Amount', 'label': 'District'})
        fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450)
        st.plotly_chart(fig3, use_container_width=True)

        # Treemap
        fig4 = px.treemap(top_dist, path=['state', 'label'], values='count',
                          title='Transaction Count Treemap — Top Districts',
                          color='amount', color_continuous_scale='Purples')
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        n_pin = st.slider("Number of top pincodes to show", 5, 20, 10)
        top_pins = top_txn[top_txn['entity_type'] == 'pincode'].groupby(['state', 'entity_name']).agg(
            count=('transaction_count', 'sum'),
            amount=('transaction_amount', 'sum')
        ).reset_index().sort_values('count', ascending=False).head(n_pin)
        top_pins['label'] = top_pins['entity_name'] + ' (' + top_pins['state'] + ')'

        fig5 = px.bar(top_pins, x='count', y='label', orientation='h',
                      title=f'Top {n_pin} Pincodes by Transaction Count',
                      color='count', color_continuous_scale='Oranges',
                      labels={'count': 'Transaction Count', 'label': 'Pincode (State)'})
        fig5.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig5, use_container_width=True)

    # Year-Quarter best performer
    st.markdown("### Best Performing Year-Quarter Combinations")
    best_qtr = top_txn.groupby(['year', 'quarter']).agg(
        count=('transaction_count', 'sum')
    ).reset_index().sort_values('count', ascending=False).head(8)
    best_qtr['label'] = best_qtr['year'].astype(str) + ' Q' + best_qtr['quarter'].astype(str)
    fig6 = px.bar(best_qtr, x='label', y='count',
                  title='Top 8 Year-Quarter by Total Transactions',
                  color='count', color_continuous_scale='Purples',
                  labels={'count': 'Transaction Count', 'label': 'Year-Quarter'})
    st.plotly_chart(fig6, use_container_width=True)

    st.info("""
    ** Key Insights:**
    - **Bengaluru Urban** is the #1 district by transaction amount — nearly 2x Hyderabad
    - Pincode **500034 (Hyderabad)** processes the most transactions of any pincode in India
    - **2024 Q4** is the best performing quarter ever recorded
    """)

# ══════════════════════════════════════════════
# PAGE 6: CASE 8 — USER REGISTRATION
# ══════════════════════════════════════════════
elif page == "Case 8: User Registration":
    st.title("Case 8: User Registration Analysis")
    st.markdown("*Finding the top states, districts, and pincodes for user onboarding.*")
    st.markdown("---")

    # Year-Quarter filter
    col_f1, col_f2 = st.columns(2)
    sel_yr = col_f1.selectbox("Select Year", sorted(top_user['year'].unique(), reverse=True))
    sel_qtr = col_f2.selectbox("Select Quarter", sorted(top_user['quarter'].unique()))

    filtered_top = top_user[(top_user['year'] == sel_yr) & (top_user['quarter'] == sel_qtr)]

    st.markdown(f"### Showing data for: **{sel_yr} Q{sel_qtr}**")

    tab1, tab2, tab3 = st.tabs(["Top States", "Top Districts", "Top Pincodes"])

    with tab1:
        st.markdown("#### Top 10 States by Registered Users")
        top_states_reg = filtered_top[filtered_top['entity_type'] == 'district'].groupby('state')['registered_users'].sum().reset_index().sort_values('registered_users', ascending=False).head(10)
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(top_states_reg, x='registered_users', y='state', orientation='h',
                         color='registered_users', color_continuous_scale='Blues',
                         labels={'registered_users': 'Registered Users', 'state': 'State'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(top_states_reg.reset_index(drop=True), use_container_width=True)

    with tab2:
        st.markdown("#### Top 10 Districts by Registered Users")
        top_dist_reg = filtered_top[filtered_top['entity_type'] == 'district'].groupby(['state', 'entity_name'])['registered_users'].sum().reset_index().sort_values('registered_users', ascending=False).head(10)
        top_dist_reg['label'] = top_dist_reg['entity_name'] + ', ' + top_dist_reg['state']
        col1, col2 = st.columns([2, 1])
        with col1:
            fig2 = px.bar(top_dist_reg, x='registered_users', y='label', orientation='h',
                          color='registered_users', color_continuous_scale='Purples',
                          labels={'registered_users': 'Users', 'label': 'District'})
            fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            st.dataframe(top_dist_reg[['label', 'registered_users']].reset_index(drop=True), use_container_width=True)

    with tab3:
        st.markdown("#### Top 10 Pincodes by Registered Users")
        top_pin_reg = filtered_top[filtered_top['entity_type'] == 'pincode'].groupby(['state', 'entity_name'])['registered_users'].sum().reset_index().sort_values('registered_users', ascending=False).head(10)
        top_pin_reg['label'] = top_pin_reg['entity_name'] + ' (' + top_pin_reg['state'] + ')'
        col1, col2 = st.columns([2, 1])
        with col1:
            fig3 = px.bar(top_pin_reg, x='registered_users', y='label', orientation='h',
                          color='registered_users', color_continuous_scale='Oranges',
                          labels={'registered_users': 'Users', 'label': 'Pincode (State)'})
            fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)
        with col2:
            st.dataframe(top_pin_reg[['label', 'registered_users']].reset_index(drop=True), use_container_width=True)

    # Overall trend
    st.markdown("### User Registration Trend Over All Quarters")
    all_reg = top_user.groupby(['year', 'quarter'])['registered_users'].sum().reset_index()
    all_reg['label'] = all_reg['year'].astype(str) + ' Q' + all_reg['quarter'].astype(str)
    all_reg = all_reg.sort_values(['year', 'quarter'])
    fig4 = px.line(all_reg, x='label', y='registered_users',
                   title='Total User Registrations — All Quarters',
                   markers=True, color_discrete_sequence=['#5f259f'])
    fig4.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

    st.info("""
    ** Key Insights:**
    - **Maharashtra** consistently leads in user registrations across all quarters
    - **Bengaluru Urban** is the #1 district for new user registrations
    - Pincode **201301 (Noida, UP)** has the highest registered users of any pincode
    - **2024 Q2** had the highest single-quarter registrations ever
    """)
