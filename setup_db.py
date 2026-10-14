import sqlite3

def setup_database():
    conn = sqlite3.connect('polyvote_relational.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Base Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ORGANIZATION (
        org_id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_name TEXT NOT NULL,
        admin_contact TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ELECTION (
        election_id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER,
        status TEXT DEFAULT 'ACTIVE',
        start_time DATETIME,
        end_time DATETIME,
        FOREIGN KEY (org_id) REFERENCES ORGANIZATION(org_id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CANDIDATE (
        candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
        election_id INTEGER,
        name TEXT NOT NULL,
        platform_statement TEXT,
        FOREIGN KEY (election_id) REFERENCES ELECTION(election_id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VOTER_PARTICIPATION (
        participation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        election_id INTEGER,
        student_reg_no TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        has_voted INTEGER DEFAULT 0 CHECK(has_voted IN (0, 1)),
        FOREIGN KEY (election_id) REFERENCES ELECTION(election_id),
        UNIQUE (student_reg_no, election_id)
    )''')

    # Enforcing strict Top-3 ranking constraint at the database layer
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BALLOT_RANKS (
        ballot_token TEXT NOT NULL,
        candidate_id INTEGER,
        election_id INTEGER,
        preference_rank INTEGER NOT NULL CHECK (preference_rank BETWEEN 1 AND 3),
        PRIMARY KEY (ballot_token, candidate_id),
        FOREIGN KEY (candidate_id) REFERENCES CANDIDATE(candidate_id),
        FOREIGN KEY (election_id) REFERENCES ELECTION(election_id)
    )''')

    # 2. Native SQL Trigger: Hard block against duplicate voting
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS trg_block_duplicate_vote
    BEFORE UPDATE OF has_voted ON VOTER_PARTICIPATION
    FOR EACH ROW
    WHEN OLD.has_voted = 1 AND NEW.has_voted = 1
    BEGIN
        SELECT RAISE(ABORT, 'DBMS Trigger Violation: Voter has already submitted a ballot.');
    END;
    ''')

    # 3. Native SQL Views: Analytics for DBA Review
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS VIEW_ELECTION_TURNOUT AS
    SELECT 
        e.election_id,
        o.org_name,
        COUNT(v.participation_id) AS total_roster,
        SUM(v.has_voted) AS total_voted,
        ROUND((CAST(SUM(v.has_voted) AS FLOAT) / COUNT(v.participation_id)) * 100, 2) AS turnout_percentage
    FROM ELECTION e
    JOIN ORGANIZATION o ON e.org_id = o.org_id
    LEFT JOIN VOTER_PARTICIPATION v ON e.election_id = v.election_id
    GROUP BY e.election_id;
    ''')

    cursor.execute('''
    CREATE VIEW IF NOT EXISTS VIEW_FIRST_PREFERENCES AS
    SELECT 
        c.candidate_id,
        c.name AS candidate_name,
        COUNT(b.ballot_token) AS first_preference_votes
    FROM CANDIDATE c
    LEFT JOIN BALLOT_RANKS b ON c.candidate_id = b.candidate_id AND b.preference_rank = 1
    GROUP BY c.candidate_id, c.name;
    ''')

    conn.commit()
    conn.close()
    print("Database configured with Top-3 constraints, Triggers, and Views.")

if __name__ == "__main__":
    setup_database()