import sqlite3
import pandas as pd

DB_PATH = 'polyvote_relational.db'

def calculate_irv_winner(election_id):
    conn = sqlite3.connect(DB_PATH)
    
    cands = pd.read_sql_query("SELECT candidate_id, name FROM CANDIDATE WHERE election_id = ?", conn, params=(election_id,))
    cand_map = dict(zip(cands['candidate_id'], cands['name']))
    
    ballots_raw = conn.execute("SELECT ballot_token, candidate_id, preference_rank FROM BALLOT_RANKS WHERE election_id = ? ORDER BY ballot_token, preference_rank", (election_id,)).fetchall()
    conn.close()

    if not ballots_raw:
        return "No votes cast yet.", None

    ballots = {}
    for token, cid, rank in ballots_raw:
        if token not in ballots:
            ballots[token] = []
        ballots[token].append(cid)
    
    active_ballots = list(ballots.values())
    active_candidates = set(cand_map.keys())
    
    round_logs = []
    round_num = 1
    
    while True:
        counts = {cid: 0 for cid in active_candidates}
        for b in active_ballots:
            if b: counts[b[0]] += 1
        
        total_votes = sum(counts.values())
        if total_votes == 0:
            return "Tie or no valid votes left.", round_logs
            
        round_df = pd.DataFrame([
            {"Candidate": cand_map[cid], "Votes": votes, "Percentage": f"{(votes/total_votes)*100:.1f}%"}
            for cid, votes in counts.items()
        ]).sort_values("Votes", ascending=False)
        
        winner_cid = None
        for cid, votes in counts.items():
            if votes > total_votes / 2:
                winner_cid = cid
                break
                
        if winner_cid:
            round_logs.append({"round": round_num, "table": round_df, "eliminated": None})
            win_msg = f"{cand_map[winner_cid]} wins with {counts[winner_cid]} votes in Round {round_num}!"
            return win_msg, round_logs
            
        lowest_cid = min(counts, key=counts.get)
        lowest_name = cand_map[lowest_cid]
        round_logs.append({"round": round_num, "table": round_df, "eliminated": lowest_name})
        
        active_candidates.remove(lowest_cid)
        for b in active_ballots:
            if lowest_cid in b: b.remove(lowest_cid)
                
        round_num += 1