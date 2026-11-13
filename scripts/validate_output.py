"""Validate the strict two-column contract using the pinned official library."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'upstream'))
import possession_metrics as pm
from games import source_frames

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv',type=Path)
    args=parser.parse_args()
    table=pm.read_label_csv(args.csv)
    reason=pm.validate_submission(table,source_frames())
    if list(table.columns)!=['frame','label']:
        reason='Expected exactly two columns, frame,label'
    if reason:
        raise SystemExit('FAIL: '+reason)
    print(f'PASS: {len(table)} rows, exact header, ordered frame IDs, valid nonblank labels.')

if __name__=='__main__':
    main()
