"""Fail closed on restricted assets in the Git index or reachable history."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_ROOTS={'data','data_staging','private','official','vendor_research','.venv','tmp','output'}
BAD={'.mp4','.avi','.mov','.mkv','.webm','.mp3','.wav','.zip','.xml','.npy','.npz','.pkl','.joblib','.pt','.pth'}
ALLOWED_CSV={'research/competitor_inventory.csv'}


def content_errors(data):
    try:text=data.decode('utf-8-sig')
    except UnicodeDecodeError:return ['unapproved binary content']
    result=[]
    if re.search(r'(?m)^-----BEGIN .*PRIVATE KEY-----\s*\n[A-Za-z0-9+/=]{30,}',text):result.append('private key')
    if re.search(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|AKIA[0-9A-Z]{16})\b',text):result.append('likely credential')
    if text.startswith('frame,label\n') or text.startswith('frame,label\r\n'):result.append('frame prediction CSV content')
    if len(re.findall(r'(?m)^\d+:[^:\n]+:[^:\n]+$',text))>=100:result.append('tracking-row content')
    if len(re.findall(r'<Frame\s',text))>=100:result.append('frame XML content')
    return result


def path_error(name):
    p=Path(name)
    if name.split('/')[0].casefold() in PRIVATE_ROOTS:return 'private directory'
    if p.suffix.lower() in BAD:return 'restricted/raw/binary format'
    if p.suffix.lower()=='.csv' and name not in ALLOWED_CSV:return 'prediction/data CSV'
    if p.suffix.lower()=='.txt' and not p.name.startswith('requirements'):return 'unapproved text/data export'
    if p.suffix.lower()=='.pdf':return 'binary PDF; release document stays local'
    if 'private' in p.name.casefold():return 'private diagnostic filename'


def main():
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
    names=git('ls-files','-z').decode().split('\0');names=[n for n in names if n]
    problems=[];manifest=[]
    for name in names:
        issue=path_error(name)
        if issue:problems.append(name+': '+issue)
        path=ROOT/name
        if path.stat().st_size>2_000_000:problems.append(name+': source >2MB')
        data=path.read_bytes()
        problems.extend(name+': '+e for e in content_errors(data))
        manifest.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    history=git('rev-list','--objects','--all').decode().splitlines();history_paths=[]
    for entry in history:
        if ' ' not in entry:continue
        oid,name=entry.split(' ',1);issue=path_error(name)
        if issue:problems.append('history '+name+': '+issue)
        history_paths.append(name)
    indexed=[]
    for line in git('ls-files','--stage').decode().splitlines():
        if line.startswith(('120000','160000')):problems.append('symlink/submodule in public index: '+line.split('\t')[-1])
        info,name=line.split('\t',1);indexed.append((info.split()[1],name))
    # Inspect actual staged blobs and every reachable historical blob, not only
    # current working-tree text. No blob content is printed or sent anywhere.
    objects={entry.split(' ',1)[0]:entry.split(' ',1)[1] for entry in history if ' ' in entry}
    objects.update(dict(indexed));ids=list(objects)
    raw=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(ids)+'\n').encode())
    position=0;blob_count=0
    for oid in ids:
        end=raw.index(b'\n',position);header=raw[position:end].decode().split();position=end+1
        size=int(header[2]);data=raw[position:position+size];position+=size+1
        if header[1]!='blob':continue
        blob_count+=1;name=objects[oid]
        if size>2_000_000:problems.append('indexed/history '+name+': source >2MB')
        problems.extend('indexed/history '+name+': '+e for e in content_errors(data))
    ignore_probes=['YDSE.csv','leak.xml','BAR-ATH_tactical_atd.txt','leak.mp4','leak.wav','leak.npz',
        'private/release_audit/readiness_metrics.json','submission/candidates/YDSE_v3.csv','submission/release/YDSE.pdf']
    for name in ignore_probes:
        result=subprocess.run(['git','check-ignore','--no-index','-q','--',name],cwd=ROOT)
        if result.returncode:problems.append('ignore gap: '+name)
    if problems:raise SystemExit('\n'.join(sorted(set(problems))))
    result=dict(status='PASS',tracked_index_files=len(names),reachable_objects=len(history),
        indexed_and_historical_blobs_scanned=blob_count,
        history_paths_checked=len(set(history_paths)),ignore_probes=ignore_probes,files=manifest,
        scope='Working-tree/index paths and contents, reachable history paths and blob contents; not a legal review or a guarantee against a later forced add')
    dest=ROOT/'private/release_audit';dest.mkdir(parents=True,exist_ok=True)
    (dest/'public_source_audit.json').write_text(json.dumps(result,indent=2),newline='\n')
    print(f'PASS: {len(names)} indexed files, {len(history)} reachable objects, no prohibited paths, ignore coverage verified.')
    print('No data/prediction/private diagnostics in the intended public source. Re-run immediately before any approved publication.')


if __name__=='__main__':main()
