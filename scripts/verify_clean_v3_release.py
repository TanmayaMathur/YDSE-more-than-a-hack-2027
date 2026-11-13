"""Export committed source and reproduce frozen V3 using an isolated Python venv.

Only reads the licensed inputs at --data-dir. All new outputs stay in --work-dir;
no existing candidate, source weights, historical metadata or release is rewritten.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
EXPECTED='3a27d7d90657d1e4b9485007f0d7ea1d95ac662a64d4a3fbe5c1b50daf4ef534'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--python',type=Path,required=True)
    ap.add_argument('--data-dir',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True)
    args=ap.parse_args();work=args.work_dir.resolve();work.mkdir(parents=True,exist_ok=True)
    dest=work/'source';assert not dest.exists(),'Use a new audit directory; never replace a prior export'
    dest.mkdir();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    archive=subprocess.check_output(['git','archive','--format=zip',commit],cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for member in z.infolist():
            assert (dest/member.filename).resolve().is_relative_to(dest)
        z.extractall(dest)
    env=os.environ.copy();env['PYTHONNOUSERSITE']='1';env['PYTHONPATH']=''
    env['GIT_CEILING_DIRECTORIES']=str(dest.parent)
    python=str(args.python.resolve());data=str(args.data_dir.resolve());logs=[]
    def run(arguments):
        result=subprocess.run([python,*arguments],cwd=dest,env=env,capture_output=True,text=True,encoding='utf-8')
        logs.append(dict(arguments=arguments,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
        if result.returncode:
            (work/'failure_log.json').write_text(json.dumps(logs,indent=2))
            raise RuntimeError('Clean audit failed; inspect private failure_log.json')
        return result.stdout
    isolated=json.loads(run(['-c','import sys,site,json,numpy,pandas; print(json.dumps(dict(prefix=sys.prefix,base_prefix=sys.base_prefix,user_site_enabled=site.ENABLE_USER_SITE,numpy=numpy.__file__,pandas=pandas.__file__)))']))
    assert isolated['prefix']!=isolated['base_prefix'] and not isolated['user_site_enabled']
    assert Path(isolated['numpy']).is_relative_to(Path(isolated['prefix']))
    run(['-m','pip','check']);test_output=run(['-m','pytest','-q']);print(test_output.strip(),flush=True)
    outputs=[]
    for number in [1,2]:
        out=work/f'YDSE_clean_{number}.csv'
        assert not out.exists(),'Do not overwrite a prior clean output'
        run(['scripts/generate_submission.py','--model','v3','--config','configs/audit_v3.json',
            '--data-dir',data,'--out',str(out)])
        run(['upstream/validate_submission.py',str(out)]);run(['scripts/validate_output.py',str(out)])
        digest=hashlib.sha256(out.read_bytes()).hexdigest();assert digest==EXPECTED
        outputs.append(dict(path=str(out),sha256=digest))
        print('Clean full-match run officially validated:',number,digest,flush=True)
    result=dict(status='PASS',source_export_commit=commit,isolated_environment=isolated,
        outputs=outputs,dependencies=json.loads(run(['-m','pip','list','--format=json'])),commands=logs,
        scope='Two clean-source, fresh-venv full runs; same Windows host/CPython, not cross-platform validation')
    (work/'verification.json').write_text(json.dumps(result,indent=2),newline='\n')
    print('PASS: isolated source and fresh dependencies reproduce the exact frozen V3 bytes twice.')


if __name__=='__main__':main()
