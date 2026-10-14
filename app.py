import streamlit as st
import sqlite3
import uuid
import pandas as pd
import random
from audit_ledger import append_ballot_receipt
from tally_engine import calculate_irv_winner
from election_core import get_db, hash_pw, init_admin_db, wipe_all_database_data, check_election_integrity

# PAGE SETUP & CSS
st.set_page_config(page_title="PolyVote OS", page_icon="🗳️", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0B0F17; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    [data-testid="stSidebar"] { background-color: #06090E !important; border-right: 1px solid #1E293B; }
    .phase-box { padding: 12px 18px; border-radius: 8px; border: 1px solid #334155; background: #0F172A; margin-bottom: 20px; font-size: 1rem; }
    .audit-pass { padding: 16px; border-radius: 8px; background-color: #064E3B; border: 1px solid #059669; color: #ECFDF5; }
    .audit-fail { padding: 16px; border-radius: 8px; background-color: #7F1D1D; border: 1px solid #DC2626; color: #FEF2F2; }
    </style>
""", unsafe_allow_html=True)

init_admin_db()

def load_elections():
    conn = get_db()
    df = pd.read_sql_query("SELECT e.election_id, o.org_name FROM ELECTION e JOIN ORGANIZATION o ON e.org_id = o.org_id", conn)
    conn.close()
    if df.empty: return {}
    return dict(zip(df['org_name'] + " (Election #" + df['election_id'].astype(str) + ")", df['election_id']))

# =========================================================
# SESSION STATE & SIDEBAR NAVIGATION
# =========================================================
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

st.sidebar.markdown("### 🗳️ **PolyVote OS**")
st.sidebar.caption("Ranked-Choice • Multi-Tenant • Cryptographic Ledger")
st.sidebar.markdown("---")

nav_options = ["🔒 Voter Booth"]
if st.session_state.admin_logged_in:
    nav_options.extend([
        "⚙️ System Administration", 
        "📊 Election Results & Certification",
        "🗄️ Database Management Studio",
        "🔓 Admin Logout"
    ])
else:
    nav_options.append("🔐 Admin Login")

portal_mode = st.sidebar.radio("Navigation", nav_options)
st.sidebar.markdown("---")

# =========================================================
# TAB: ADMIN LOGIN / LOGOUT
# =========================================================
if portal_mode == "🔐 Admin Login":
    st.title("🔐 Secure System Administrator Login")
    st.caption("Authorized personnel only. Default credentials: admin / admin123")
    
    with st.form("admin_login_form"):
        admin_user = st.text_input("Admin Username")
        admin_pass = st.text_input("Admin Password", type="password")
        if st.form_submit_button("Log In to Dashboard", type="primary"):
            conn = get_db()
            record = conn.execute("SELECT password_hash FROM ADMIN_USERS WHERE username = ?", (admin_user.strip(),)).fetchone()
            conn.close()
            
            if record and record[0] == hash_pw(admin_pass):
                st.session_state.admin_logged_in = True
                st.success("Authentication successful. Unlocking dashboard...")
                st.rerun()
            else:
                st.error("Invalid administrator credentials.")

elif portal_mode == "🔓 Admin Logout":
    st.session_state.admin_logged_in = False
    st.rerun()

# =========================================================
# TAB 1: SYSTEM ADMINISTRATION
# =========================================================
elif portal_mode == "⚙️ System Administration":
    st.title("⚙️ System Administration & Election Lifecycle")

    with st.expander("🧨 Danger Zone: Database Reset", expanded=False):
        if st.button("🧨 Factory Reset (Zero Out Everything)", use_container_width=True):
            wipe_all_database_data()
            st.toast("System wiped clean!", icon="🧹")
            st.rerun()

    # --- MANAGE ADMINISTRATORS ---
    st.markdown("### 👥 Manage System Administrators")
    with st.expander("➕ Add New Administrator", expanded=False):
        with st.form("add_admin_form"):
            new_admin_user = st.text_input("New Username")
            new_admin_pass = st.text_input("New Password", type="password")
            if st.form_submit_button("Create Admin"):
                if new_admin_user and new_admin_pass:
                    try:
                        conn = get_db()
                        conn.execute("INSERT INTO ADMIN_USERS (username, password_hash) VALUES (?, ?)", (new_admin_user.strip(), hash_pw(new_admin_pass)))
                        conn.commit()
                        conn.close()
                        st.success(f"Admin '{new_admin_user}' successfully created.")
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    st.markdown("---")
    
    col_new, col_manage = st.columns([1, 2])
    with col_new:
        st.markdown("### Deploy New Tenant")
        with st.form("init_form"):
            org_name = st.text_input("Organization Name", placeholder="e.g., Computer Science Society")
            admin_contact = st.text_input("Lead Administrator Email", placeholder="admin@cs.org")
            if st.form_submit_button("Deploy Instance", type="primary"):
                if org_name and admin_contact:
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO ORGANIZATION (org_name, admin_contact) VALUES (?, ?)", (org_name, admin_contact))
                    org_id = cursor.lastrowid
                    cursor.execute("INSERT INTO ELECTION (org_id, status, start_time, end_time) VALUES (?, 'NOMINATION', datetime('now'), datetime('now', '+7 days'))", (org_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"Election created for {org_name}.")
                    st.rerun()

    with col_manage:
        st.markdown("### Manage Tenant Lifecycle")
        elections = load_elections()
        if elections:
            selected_e_name = st.selectbox("Active Election Scope:", list(elections.keys()))
            e_id = elections[selected_e_name]

            conn = get_db()
            e_status = conn.execute("SELECT status FROM ELECTION WHERE election_id = ?", (e_id,)).fetchone()[0]
            
            st.markdown(f'<div class="phase-box"><strong>Current Phase:</strong> <code>{e_status}</code></div>', unsafe_allow_html=True)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if e_status == 'NOMINATION':
                    if st.button("🔒 Lock Nominations & Open Voting", use_container_width=True, type="primary"):
                        conn.execute("UPDATE ELECTION SET status = 'VOTING' WHERE election_id = ?", (e_id,))
                        conn.commit(); st.rerun()
            with c_btn2:
                if e_status == 'VOTING':
                    if st.button("🛑 End Election & Close Voting", use_container_width=True, type="primary"):
                        conn.execute("UPDATE ELECTION SET status = 'CLOSED' WHERE election_id = ?", (e_id,))
                        conn.commit(); st.rerun()

            st.markdown("---")
            mc1, mc2 = st.columns(2)
            
            with mc1:
                st.markdown("#### 1. Candidates")
                if e_status == 'NOMINATION':
                    tab_auto_c, tab_man_c = st.tabs(["⚡ Auto-Generate", "✏️ Manual Entry"])
                    
                    with tab_auto_c:
                        with st.form("auto_cand_form"):
                            c_num = st.number_input("Candidates to Seed", min_value=1, max_value=5, value=4)
                            if st.form_submit_button("Seed Candidates"):
                                candidates = [('Arun Kumar', 'Academics'), ('Bhavya Singh', 'Sports'), ('Chaitanya Reddy', 'Hostels'), ('Diya Sharma', 'Tech'), ('Eshaan Iyer', 'Environment')]
                                conn.executemany("INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (?, ?, ?)", [(e_id, n, s) for n, s in candidates[:c_num]])
                                conn.commit(); st.rerun()
                                
                    with tab_man_c:
                        with st.form("manual_cand_form"):
                            c_name = st.text_input("Candidate Name")
                            c_platform = st.text_input("Platform")
                            if st.form_submit_button("Insert Candidate"):
                                if c_name:
                                    conn.execute("INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (?, ?, ?)", (e_id, c_name.strip(), c_platform.strip()))
                                    conn.commit(); st.rerun()
                
                c_df = pd.read_sql_query("SELECT candidate_id AS ID, name AS Candidate FROM CANDIDATE WHERE election_id = ?", conn, params=(e_id,))
                st.dataframe(c_df, use_container_width=True, hide_index=True)

            with mc2:
                st.markdown("#### 2. Roster Management")
                if e_status in ['NOMINATION', 'VOTING']:
                    tab_auto_v, tab_man_v = st.tabs(["⚡ Auto-Register", "✏️ Manual Authorization"])
                    
                    with tab_auto_v:
                        with st.form("auto_voter_form"):
                            t_voters = st.number_input("Students to Authorize (Pass: vote123)", min_value=1, max_value=1000, value=25)
                            if st.form_submit_button("Bulk Register"):
                                existing = conn.execute("SELECT COUNT(*) FROM VOTER_PARTICIPATION WHERE election_id = ?", (e_id,)).fetchone()[0]
                                voters = [(e_id, f'25BCE{str(existing + i).zfill(4)}', hash_pw('vote123'), 0) for i in range(1, t_voters + 1)]
                                conn.executemany("INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?, ?, ?, ?)", voters)
                                conn.commit(); st.rerun()

                    with tab_man_v:
                        with st.form("manual_voter_form"):
                            v_reg = st.text_input("Registration No.", placeholder="e.g., 25BCE9999")
                            v_pass = st.text_input("Assign Custom Password", type="password")
                            if st.form_submit_button("Authorize Individual Voter"):
                                if v_reg and v_pass:
                                    try:
                                        conn.execute("INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?, ?, ?, 0)", (e_id, v_reg.strip().upper(), hash_pw(v_pass)))
                                        conn.commit(); st.success(f"Added {v_reg.upper()}!"); st.rerun()
                                    except sqlite3.IntegrityError: st.error("Voter already exists in roster.")

                v_df = pd.read_sql_query("SELECT student_reg_no AS Registration_No, has_voted AS Voted FROM VOTER_PARTICIPATION WHERE election_id = ? ORDER BY participation_id DESC LIMIT 5", conn, params=(e_id,))
                st.caption("Latest 5 Registered Voters:")
                st.dataframe(v_df, use_container_width=True, hide_index=True)

                if e_status == 'VOTING':
                    st.markdown("---")
                    st.markdown("#### 🗳️ Batch Ballot Simulation")
                    with st.form("vote_simulator"):
                        sim_count = st.number_input("Random Ballots to Simulate", min_value=1, max_value=1000, value=20)
                        if st.form_submit_button("Simulate Ballots", type="primary"):
                            unvoted = conn.execute("SELECT participation_id, student_reg_no FROM VOTER_PARTICIPATION WHERE election_id = ? AND has_voted = 0 LIMIT ?", (e_id, sim_count)).fetchall()
                            cand_ids = [row[0] for row in conn.execute("SELECT candidate_id FROM CANDIDATE WHERE election_id = ?", (e_id,)).fetchall()]
                            
                            if len(cand_ids) < 3: st.error("Need 3 candidates to cast Top-3 ranked votes.")
                            elif not unvoted: st.error("No unvoted students remaining.")
                            else:
                                for pid, reg in unvoted:
                                    token = str(uuid.uuid4())
                                    conn.execute("UPDATE VOTER_PARTICIPATION SET has_voted = 1 WHERE participation_id = ?", (pid,))
                                    ranks_to_pick = min(3, len(cand_ids))
                                    chosen = random.sample(cand_ids, ranks_to_pick)
                                    payload = [(chosen[i], i+1) for i in range(ranks_to_pick)]
                                    for cid, rank in payload:
                                        conn.execute("INSERT INTO BALLOT_RANKS (ballot_token, candidate_id, election_id, preference_rank) VALUES (?, ?, ?, ?)", (token, cid, e_id, rank))
                                    append_ballot_receipt(e_id, token, payload)
                                conn.commit(); st.rerun()
            conn.close()

# =========================================================
# TAB 2: VOTER BOOTH (Publicly Accessible)
# =========================================================
elif portal_mode == "🔒 Voter Booth":
    st.title("🔒 Official Voter Booth")
    elections = load_elections()
    if not elections: st.info("Welcome to PolyVote. Please wait for an administrator to deploy an election.")
    else:
        if 'voter_logged_in' not in st.session_state: st.session_state.voter_logged_in = False
        if not st.session_state.voter_logged_in:
            col_auth, _ = st.columns([1, 1])
            with col_auth:
                selected_e_name = st.selectbox("Select Election Context:", list(elections.keys()))
                e_id = elections[selected_e_name]
                conn = get_db()
                e_status = conn.execute("SELECT status FROM ELECTION WHERE election_id = ?", (e_id,)).fetchone()[0]
                conn.close()

                if e_status == 'NOMINATION': st.warning("Voting is currently closed.")
                elif e_status == 'CLOSED': st.error("Election permanently closed.")
                else:
                    reg_input = st.text_input("Registration Number")
                    pass_input = st.text_input("Access Password", type="password")
                    if st.button("Authenticate & Enter Booth", type="primary"):
                        conn = get_db()
                        record = conn.execute("SELECT participation_id, password_hash, has_voted FROM VOTER_PARTICIPATION WHERE student_reg_no = ? AND election_id = ?", (reg_input.strip().upper(), e_id)).fetchone()
                        conn.close()
                        if not record: st.error("Not found in roster.")
                        elif record[1] != hash_pw(pass_input): st.error("Invalid password.")
                        elif record[2] == 1: st.error("🚫 You have already voted.")
                        else:
                            st.session_state.voter_logged_in = True
                            st.session_state.voter_id = record[0]
                            st.session_state.reg_no = reg_input.strip().upper()
                            st.session_state.e_id = e_id
                            st.rerun()
        else:
            e_id = st.session_state.e_id
            st.success(f"Authenticated: **{st.session_state.reg_no}**")
            conn = get_db()
            c_df = pd.read_sql_query("SELECT candidate_id, name FROM CANDIDATE WHERE election_id = ?", conn, params=(e_id,))
            conn.close()

            st.markdown("### Cast Your Ranked Ballot")
            c_names = c_df['name'].tolist()
            n2i = dict(zip(c_df['name'], c_df['candidate_id']))
            r1 = st.selectbox("1st Preference (Rank 1)", c_names, index=0)
            r2 = st.selectbox("2nd Preference (Rank 2)", c_names, index=1)
            r3 = st.selectbox("3rd Preference (Rank 3)", c_names, index=2)

            if st.button("Submit Encrypted Ballot", type="primary"):
                if len(set([r1, r2, r3])) < 3: st.error("Distinct candidates required.")
                else:
                    ballot_token = str(uuid.uuid4())
                    payload = [(n2i[r1], 1), (n2i[r2], 2), (n2i[r3], 3)]
                    conn = get_db()
                    conn.execute("UPDATE VOTER_PARTICIPATION SET has_voted = 1 WHERE participation_id = ?", (st.session_state.voter_id,))
                    for cid, rank in payload:
                        conn.execute("INSERT INTO BALLOT_RANKS (ballot_token, candidate_id, election_id, preference_rank) VALUES (?, ?, ?, ?)", (ballot_token, cid, e_id, rank))
                    conn.commit()
                    append_ballot_receipt(e_id, ballot_token, payload)
                    st.success(f"✅ Ballot cast! Token: `{ballot_token}`")
                    st.session_state.voter_logged_in = False
                    conn.close()

# =========================================================
# TAB 3: ELECTION RESULTS & AUDIT (Requires Login)
# =========================================================
elif portal_mode == "📊 Election Results & Certification":
    st.title("📊 Official Results & Security Audit")
    st.caption("Election officials and voters view this page to verify tallies and system integrity.")
    elections = load_elections()
    if not elections: st.warning("No elections available.")
    else:
        selected_e_name = st.selectbox("Election Context:", list(elections.keys()))
        e_id = elections[selected_e_name]
        conn = get_db()

        st.markdown("### Step 1: Execute Forensic Integrity Sweep")
        st.caption("Before declaring a winner, the system checks if the SQL Database matches the Cryptographic Ledger.")
        
        if st.button("🛡️ Run System Integrity Sweep", use_container_width=True, type="primary"):
            is_valid, msg, report = check_election_integrity(e_id)
            if is_valid:
                st.markdown(f'<div class="audit-pass"><strong>🟢 ELECTION CERTIFIED:</strong> Relational SQL records match the immutable cryptographic ledger. 0 discrepancies detected.</div>', unsafe_allow_html=True)
            else:
                total_flags = len(report['modified']) + len(report['deleted'])
                st.markdown(f'<div class="audit-fail"><strong>🚨 CONTESTED / TAMPERED:</strong> Relational database has been compromised! {total_flags} ballot record(s) fail cryptographic ledger verification.</div>', unsafe_allow_html=True)
                
                # --- NEW FORENSIC INCIDENT TABLE ---
                st.markdown("#### 🔎 Forensic Incident Log")
                st.caption("Detailed breakdown of database anomalies detected by the cryptographic ledger.")
                
                forensic_data = []
                for token in report['modified']:
                    forensic_data.append({"Ballot Token (Truncated)": f"{token[:12]}...", "Anomaly Type": "⚠️ MODIFIED", "Forensic Detail": "Hash mismatch. DBA altered candidate ranks."})
                for token in report['deleted']:
                    forensic_data.append({"Ballot Token (Truncated)": f"{token[:12]}...", "Anomaly Type": "🗑️ DELETED", "Forensic Detail": "Record missing from SQL. DBA suppressed vote."})
                
                df_forensics = pd.DataFrame(forensic_data)
                
                # Render as a clean dataframe
                st.dataframe(
                    df_forensics, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Anomaly Type": st.column_config.TextColumn(width="small"),
                        "Ballot Token (Truncated)": st.column_config.TextColumn(width="medium")
                    }
                )

        st.markdown("---")
        st.markdown("### Step 2: Instant-Runoff Tally")
        
        col_irv, col_fp = st.columns([1, 1])
        with col_irv:
            if st.button("🚀 Calculate Final Winner", use_container_width=True):
                result = calculate_irv_winner(e_id)
                if isinstance(result, tuple):
                    win_msg, round_logs = result
                    st.success(f"🏆 **WINNER:** {win_msg}")
                    with st.expander("📊 Inspect Round-by-Round Breakdown", expanded=True):
                        for log in round_logs:
                            st.markdown(f"##### Round {log['round']}")
                            st.dataframe(log['table'], use_container_width=True, hide_index=True)
                            if log['eliminated']: st.error(f"❌ {log['eliminated']} eliminated.")
                else: st.info(result)

        with col_fp:
            st.caption("Current 1st-Preference Votes (Relational State)")
            fp_df = pd.read_sql_query("SELECT c.name AS Candidate, COUNT(b.ballot_token) AS First_Preference_Votes FROM CANDIDATE c LEFT JOIN BALLOT_RANKS b ON c.candidate_id = b.candidate_id AND b.preference_rank = 1 WHERE c.election_id = ? GROUP BY c.candidate_id ORDER BY First_Preference_Votes DESC", conn, params=(e_id,))
            st.dataframe(fp_df, use_container_width=True, hide_index=True)
        conn.close()

# =========================================================
# TAB 4: DATABASE MANAGEMENT STUDIO (Requires Login)
# =========================================================
elif portal_mode == "🗄️ Database Management Studio":
    st.title("🗄️ Database Management Studio")
    st.caption("🚨 NOTE FOR EVALUATORS: In a production environment, this page does not exist in the web app. It visually simulates the raw backend access a Database Administrator has via tools like pgAdmin, DBeaver, or AWS RDS.")
    
    elections = load_elections()
    if not elections:
        st.warning("No elections available.")
    else:
        selected_e_name = st.selectbox("Election Context:", list(elections.keys()))
        e_id = elections[selected_e_name]
        conn = get_db()
        
        # --- TABLE 1: CANDIDATES ---
        st.markdown("---")
        st.subheader("1. Object Explorer: `CANDIDATES` Table")
        st.caption("Standard Maintenance: Double-click a name to fix a typo. (Cryptographic seals ignore display names).")
        
        cand_df = pd.read_sql_query("SELECT candidate_id, name, platform_statement FROM CANDIDATE WHERE election_id = ?", conn, params=(e_id,))
        edited_cand = st.data_editor(
            cand_df, disabled=["candidate_id"], use_container_width=True, hide_index=True, key="cand_editor"
        )
        
        # --- TABLE 2: VOTER PARTICIPATION (ROSTER) ---
        st.markdown("---")
        st.subheader("2. Object Explorer: `VOTER_PARTICIPATION` Table")
        st.caption("Standard Maintenance: Double-click a Registration No. to fix a typo. To remove a voter, check 'Drop_Voter'.")
        
        voter_df = pd.read_sql_query("SELECT participation_id, student_reg_no, has_voted FROM VOTER_PARTICIPATION WHERE election_id = ?", conn, params=(e_id,))
        voter_df['Drop_Voter'] = False # Checkbox column for deletion
        
        edited_voters = st.data_editor(
            voter_df, disabled=["participation_id", "has_voted"], num_rows="fixed", use_container_width=True, hide_index=True, key="voter_editor"
        )

        # --- TABLE 3: BALLOT RANKS (VOTES) ---
        st.markdown("---")
        st.subheader("3. Object Explorer: `BALLOT_RANKS` Table")
        st.markdown("**Identity Decoupling Active:** The DBA can see the votes, but *cannot* see the voter IDs. The Secret Ballot holds.")
        st.caption("Data Alteration: Double-click a `candidate_id` to assign a vote to someone else. To suppress a vote, check 'Delete_Vote'.")
        
        ballot_df = pd.read_sql_query("SELECT ballot_token, candidate_id, preference_rank FROM BALLOT_RANKS WHERE election_id = ? ORDER BY ballot_token, preference_rank LIMIT 90", conn, params=(e_id,))
        ballot_df['Delete_Vote'] = False # Checkbox column for deletion
        
        edited_ballots = st.data_editor(
            ballot_df, disabled=["ballot_token", "preference_rank"], num_rows="fixed", use_container_width=True, hide_index=True, key="ballot_editor"
        )
        
        # --- SINGLE UNIVERSAL SAVE BUTTON ---
        if st.button("💾 Commit Database Changes", type="primary"):
            has_errors = False
            
            # 1. Save Candidate Changes
            for index, row in edited_cand.iterrows():
                conn.execute("UPDATE CANDIDATE SET name = ?, platform_statement = ? WHERE candidate_id = ? AND election_id = ?", (row['name'], row['platform_statement'], row['candidate_id'], e_id))
            
            # 2. Save Voter Deletions and Updates
            for index, row in edited_voters.iterrows():
                if row.get('Drop_Voter', False):
                    conn.execute("DELETE FROM VOTER_PARTICIPATION WHERE participation_id = ?", (row['participation_id'],))
                else:
                    try:
                        conn.execute("UPDATE VOTER_PARTICIPATION SET student_reg_no = ? WHERE participation_id = ?", (row['student_reg_no'], row['participation_id']))
                    except sqlite3.IntegrityError:
                        st.error(f"Error: Registration No. {row['student_reg_no']} already exists in the roster.")
                        has_errors = True
            
            # 3. Save Ballot Updates and Deletions
            for index, row in edited_ballots.iterrows():
                if row.get('Delete_Vote', False):
                    conn.execute("DELETE FROM BALLOT_RANKS WHERE ballot_token = ? AND preference_rank = ?", (row['ballot_token'], row['preference_rank']))
                else:
                    try:
                        conn.execute("UPDATE BALLOT_RANKS SET candidate_id = ? WHERE ballot_token = ? AND preference_rank = ?", (row['candidate_id'], row['ballot_token'], row['preference_rank']))
                    except sqlite3.IntegrityError:
                        st.error(f"Error: Could not reassign ballot `{row['ballot_token'][:8]}...` to Candidate {row['candidate_id']}. That candidate is already ranked as another choice on this specific ballot.")
                        has_errors = True
                        continue
                    
            conn.commit()
            if not has_errors:
                st.success("Database changes successfully committed.")
                st.rerun()
            
        conn.close()