import sqlite3
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    conn = sqlite3.connect('polyvote_relational.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Insert Organization
    cursor.execute('''
        INSERT INTO ORGANIZATION (org_name, admin_contact)
        VALUES (?, ?)
    ''', ('VIT Student Council', 'council@vit.ac.in'))
    org_id = cursor.lastrowid

    # 2. Insert Election
    cursor.execute('''
        INSERT INTO ELECTION (org_id, status, start_time, end_time)
        VALUES (?, 'ACTIVE', datetime('now'), datetime('now', '+7 days'))
    ''', (org_id,))
    election_id = cursor.lastrowid

    # 3. Insert Candidates
    candidates = [
        ('Alice Chen', 'Advocating for 24/7 library access and better lab infrastructure.'),
        ('Bob Smith', 'Focusing on transparent student budget allocation and campus clubs.'),
        ('Charlie Patel', 'Committed to expanding tech symposiums and hackathon funding.'),
        ('Diana Roy', 'Promoting sustainable green campus initiatives and student wellness.')
    ]
    cursor.executemany('''
        INSERT INTO CANDIDATE (election_id, name, platform_statement)
        VALUES (?, ?, ?)
    ''', [(election_id, name, statement) for name, statement in candidates])

    # 4. Insert 25 Mock Registered Voters
    # Default password for all mock voters is 'vote123'
    default_hash = hash_password('vote123')
    voters = [
        (election_id, f'25BCE{str(i).zfill(4)}', default_hash, 0)
        for i in range(1, 26)
    ]
    cursor.executemany('''
        INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted)
        VALUES (?, ?, ?, ?)
    ''', voters)

    conn.commit()
    conn.close()

    print("--- Database Seeded Successfully! ---")
    print(f"Organization ID: {org_id} ('VIT Student Council')")
    print(f"Election ID: {election_id} (Status: ACTIVE)")
    print("Candidates Added: Alice Chen, Bob Smith, Charlie Patel, Diana Roy")
    print("Mock Voters Created: 25 students (25BCE0001 through 25BCE0025)")
    print("Default voter password for testing: vote123\n")

if __name__ == "__main__":
    seed_database()