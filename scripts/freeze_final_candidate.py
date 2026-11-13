"""Freeze inference source, learned weights and config before new evaluation outcomes."""
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'research/final_accuracy/candidate_freeze.json'
FILES=['src/possession/data.py','src/possession/official.py','src/possession/preprocessing.py',
       'src/possession/features.py','src/possession/tagging.py','src/possession/restarts.py',
       'src/possession/temporal.py','src/possession/pipeline.py','src/possession/v2.py',
       'src/possession/learned_dead.py','src/possession/live_dead_experiment.py','src/possession/v3.py',
       'src/possession/final_scenarios.py','configs/audit_v3.json','models/ydse_live_dead.json']

def text_hash(path):
    return hashlib.sha256(Path(path).read_text(encoding='utf-8').encode('utf-8')).hexdigest()

def current():return {name:text_hash(ROOT/name) for name in FILES}
def verify_freeze():
    frozen=json.loads(PATH.read_text());assert frozen['files']==current(),'Frozen source/config/weights changed after evaluation lock'
    return frozen
def main():
    if PATH.exists():verify_freeze();print('Freeze verified; unchanged.');return
    record=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),files=current(),
        hash_method='UTF-8 text normalized to LF',
        training_match='J03WOH (development)',new_evaluation_matches=['J03WQQ','J03WN1'],
        selected_mode='blend',decision_basis='Development half split plus fixture-valid stress guard; no new match outcomes read',
        restriction='Do not refit/change this candidate after inspecting the new match outcomes')
    PATH.write_text(json.dumps(record,indent=2));print('Candidate source, config, weights and stress design frozen before new evaluation outcomes.')
if __name__=='__main__':main()
