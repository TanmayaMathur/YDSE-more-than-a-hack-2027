"""Fetch one preselected CC BY 4.0 OTHER match, never reads competition files."""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
# Selected for smallest tracking file, before inspecting model outcomes.
MATCH='J03WOH';FILE_IDS=(51643478,51643520)

def main():
    folder=ROOT/'private/accuracy_audit/external_dfl';folder.mkdir(parents=True,exist_ok=True)
    article=json.load(urllib.request.urlopen('https://api.figshare.com/v2/articles/28196177',timeout=30))
    assert article['license']['url']=='https://creativecommons.org/licenses/by/4.0/'
    (folder/'article.json').write_text(json.dumps(article,indent=2))
    records=[]
    for file in article['files']:
        if file['id'] not in FILE_IDS:continue
        path=folder/file['name']
        if not path.exists():
            temp=path.with_suffix('.download')
            if temp.exists():raise FileExistsError('Previous partial external download; inspect before retry')
            with urllib.request.urlopen(file['download_url'],timeout=90) as src,temp.open('xb') as dst:
                shutil.copyfileobj(src,dst,length=1024*1024)
            if temp.stat().st_size!=file['size']:raise ValueError('External download size mismatch')
            temp.rename(path)
        digest=hashlib.md5(path.read_bytes()).hexdigest()
        expected=file.get('computed_md5') or file.get('supplied_md5')
        if expected and digest!=expected:raise ValueError('External checksum mismatch')
        records.append({'id':file['id'],'name':file['name'],'bytes':path.stat().st_size,'md5':digest})
        print('Verified public external asset:',file['id'],path.stat().st_size,'bytes',flush=True)
    (folder/'manifest.json').write_text(json.dumps({'match':MATCH,'licence':article['license'],'files':records},indent=2))

if __name__=='__main__':main()
