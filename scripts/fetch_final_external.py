"""Download only preselected, CC BY 4.0 other-match assets; no competition reads."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
FILES={'J03WQQ':(51643484,51643529),'J03WN1':(51643472,51643517)}

def digest(path,algorithm='md5'):
    h=hashlib.new(algorithm)
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    dest=ROOT/'private/final_accuracy/external';dest.mkdir(parents=True,exist_ok=True)
    article=json.load(urllib.request.urlopen('https://api.figshare.com/v2/articles/28196177',timeout=30))
    assert article['license']['url']=='https://creativecommons.org/licenses/by/4.0/'
    (dest/'article.json').write_text(json.dumps(article,indent=2))
    tasks=[(match,f) for match,ids in FILES.items() for f in article['files'] if f['id'] in ids]
    def get(task):
        match,f=task;folder=dest/match;folder.mkdir(exist_ok=True);path=folder/f['name']
        if not path.exists():
            partial=path.with_suffix('.download')
            if partial.exists():raise FileExistsError('Partial download exists; inspect before retry')
            total=0;milestone=32*1024**2
            with urllib.request.urlopen(f['download_url'],timeout=90) as src,partial.open('xb') as out:
                while block:=src.read(1024*1024):
                    out.write(block);total+=len(block)
                    if total>=milestone:
                        print(f'{match}: {total//1024**2} MiB received',flush=True);milestone+=32*1024**2
            if partial.stat().st_size!=f['size']:raise ValueError('Download size mismatch')
            partial.rename(path)
        checksum=digest(path);expected=f.get('computed_md5') or f.get('supplied_md5')
        if expected and checksum!=expected:raise ValueError('Download checksum mismatch')
        print(f'Verified external asset {match}: {f["id"]}, {f["size"]} bytes',flush=True)
        return {'match':match,'id':f['id'],'name':f['name'],'bytes':f['size'],'md5':checksum}
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(get,tasks))
    (dest/'manifest.json').write_text(json.dumps({'licence':article['license'],'files':records},indent=2))

if __name__=='__main__':main()
