"""Repeatable public-only GitHub intelligence. Requires gh; never reads match data."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = 'metrica-sports/more-than-a-hack-2027'
QUERIES = ['more-than-a-hack-2027', 'more-than-a-hack', 'morethanahack', '"more than a hack"',
           'MTAH2027', '"MTAH 2027"', 'mtah-2027-possession', 'mtah possession',
           'metrica sports hackathon', 'Barcelona possession hackathon', 'FC Barcelona football hackathon',
           'Barca possession AI', 'football possession segmentation', 'football ball ownership',
           'football spellF1', 'soccer tracking possession', '"BAR-ATH" possession',
           '"possession_metrics.py"', 'Metrica sports ball possession', 'Talent Arena 2027 hackathon']
LEADS = ['darfattt/mtah-2027-possession', 'DivyanshAfk/mtah-2027-possession']
STRONG = LEADS + ['yassintamer91/more-than-a-hack-2027', 'hnfadtya/more-than-a-hack-2027',
                 'aditwidi/more-than-a-hack-2027-team-nexus', 'ArmicZeroGTRS/more-than-a-hack-2027',
                 '4139benuzter/mtah2027-mas-bueno', 'Opus-Operandi-FC-Barcelona/mtah2027-possession-engine',
                 'Opus-Operandi-FC-Barcelona/mtah2027-external-benchmarks']

def api(endpoint, paginate=False):
    cmd = ['gh', 'api', endpoint]
    if paginate:
        cmd += ['--paginate', '--slurp']
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        return {'error': result.stderr.strip(), 'endpoint': endpoint}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {'error': 'Invalid API JSON', 'endpoint': endpoint}
    if paginate and isinstance(data, list) and all(isinstance(p, list) for p in data):
        return [row for page in data for row in page]
    return data

def list_api(suffix):
    sep = '&' if '?' in suffix else '?'
    return api(f'repos/{OFFICIAL}/{suffix}{sep}per_page=100', True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='Skip broad search and per-fork comparison')
    args = parser.parse_args()
    folder = ROOT / 'research' / 'github_updates'
    raw = folder / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    previous_path = raw / 'latest.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
    stamp = datetime.now(timezone.utc).isoformat()
    scan = {'timestamp_utc': stamp, 'official': api('repos/' + OFFICIAL)}
    endpoints = ['branches', 'tags', 'commits', 'issues?state=all', 'pulls?state=all',
                 'issues/comments', 'pulls/comments', 'comments', 'releases', 'forks', 'actions/workflows']
    with ThreadPoolExecutor(max_workers=5) as pool:
        for key, value in zip(endpoints, pool.map(list_api, endpoints)):
            scan[key] = value
    scan['commit_details'] = {}
    for commit in scan.get('commits', []) if isinstance(scan.get('commits'), list) else []:
        scan['commit_details'][commit['sha']] = api(f'repos/{OFFICIAL}/commits/{commit["sha"]}')
    scan['pull_details'] = {}
    for pr in scan.get('pulls?state=all', []) if isinstance(scan.get('pulls?state=all'), list) else []:
        n = pr['number']
        scan['pull_details'][str(n)] = {key: api(f'repos/{OFFICIAL}/pulls/{n}/{key}?per_page=100', True)
                                       for key in ['files', 'reviews', 'comments', 'commits']}
        scan['pull_details'][str(n)]['issue_comments'] = api(f'repos/{OFFICIAL}/issues/{n}/comments?per_page=100', True)
    # All issue comments are fetched globally; per-PR comments above preserve review context.
    competitors = {repo: api('repos/' + repo) for repo in STRONG}
    org = api('users/Opus-Operandi-FC-Barcelona/repos?per_page=100', True)
    scan['lead_organisation'] = org
    if isinstance(org, list):
        for repo in org:
            competitors[repo['full_name']] = repo
    if not args.quick:
        scan['searches'] = {}
        for query in QUERIES:
            result = api('search/repositories?q=' + quote(query + ' in:name,description,readme') + '&per_page=100')
            scan['searches'][query] = result
            if isinstance(result, dict):
                for repo in result.get('items', []):
                    competitors[repo['full_name']] = repo
            time.sleep(2.1)  # search has a separate 30/minute quota
    elif isinstance(previous.get('competitors'), dict):
        competitors = previous['competitors'] | competitors
        scan['searches'] = previous.get('searches', {})
    scan['competitors'] = competitors
    forks = scan.get('forks', [])
    scan['fork_comparisons'] = {}
    if isinstance(forks, list) and not args.quick:
        def compare(fork):
            endpoint = f'repos/{OFFICIAL}/compare/main...{fork["owner"]["login"]}:{fork["default_branch"]}'
            result = api(endpoint)
            return fork['full_name'], {key: result.get(key) for key in
                                      ['status', 'ahead_by', 'behind_by', 'total_commits', 'html_url', 'error']} | {
                                      'files': [{k: f.get(k) for k in ['filename', 'status', 'additions', 'deletions']}
                                                for f in result.get('files', [])]}
        with ThreadPoolExecutor(max_workers=5) as pool:
            for name, comparison in pool.map(compare, forks):
                scan['fork_comparisons'][name] = comparison
    elif args.quick:
        scan['fork_comparisons'] = previous.get('fork_comparisons', {})
        old_forks={f['full_name']:f for f in previous.get('forks',[])}
        for fork in forks if isinstance(forks,list) else []:
            old=old_forks.get(fork['full_name'],{})
            if old.get('pushed_at')!=fork.get('pushed_at'):
                result=api(f'repos/{OFFICIAL}/compare/main...{fork["owner"]["login"]}:{fork["default_branch"]}')
                scan['fork_comparisons'][fork['full_name']]={
                    k:result.get(k) for k in ['status','ahead_by','behind_by','total_commits','html_url','error']}
                scan['fork_comparisons'][fork['full_name']]['files']=[
                    {k:f.get(k) for k in ['filename','status','additions','deletions']} for f in result.get('files',[])]
    scan['rate_limit'] = api('rate_limit')
    changed = []
    for key, value in scan.items():
        if key not in ('timestamp_utc', 'rate_limit') and value != previous.get(key):
            changed.append(key)
    filename = stamp[:19].replace(':', '-')
    payload = json.dumps(scan, indent=2, ensure_ascii=False)
    (raw / (filename + '.json')).write_text(payload, encoding='utf-8')
    previous_path.write_text(payload, encoding='utf-8')
    def count(key):
        return len(scan[key]) if isinstance(scan.get(key), list) else 'inaccessible'
    lines = ['# Public GitHub update scan', '', f'UTC: {stamp}',
             f'Official: https://github.com/{OFFICIAL}', '',
             f'Commits: {count("commits")}; issues (including PRs): {count("issues?state=all")}; '
             f'PRs: {count("pulls?state=all")}; forks: {count("forks")}.',
             'Changed sections: ' + ', '.join(changed), '',
             'Raw public API evidence is kept locally in research/github_updates/raw/.',
             'No restricted match files are read by this script.', '', '## Changed official commits']
    old_shas = {c['sha'] for c in previous.get('commits', [])} if isinstance(previous.get('commits', []), list) else set()
    for c in scan.get('commits', []) if isinstance(scan.get('commits'), list) else []:
        if c['sha'] not in old_shas:
            lines.append(f'- {c["sha"]}: {c["commit"]["message"]} — {c["html_url"]}')
    lines+=['','## New or changed issues, PRs and comments']
    for key in ['issues?state=all','pulls?state=all','issues/comments','pulls/comments','comments']:
        current=scan.get(key); old=previous.get(key,[])
        if not isinstance(current,list):
            continue
        old_by_id={r.get('id'):r for r in old if isinstance(r,dict)} if isinstance(old,list) else {}
        for row in current:
            if isinstance(row,dict) and row!=old_by_id.get(row.get('id')):
                lines.append(f'- {key}: {row.get("title",row.get("id"))} — {row.get("html_url","")}')
    lines+=['','## Meaningful fork and competitor updates']
    for name,comparison in scan['fork_comparisons'].items():
        if comparison.get('ahead_by') and comparison!=previous.get('fork_comparisons',{}).get(name):
            lines.append(f'- Fork {name}: {comparison["ahead_by"]} commits ahead — https://github.com/{name}')
    for name,repo in competitors.items():
        if repo.get('pushed_at')!=previous.get('competitors',{}).get(name,{}).get('pushed_at'):
            lines.append(f'- {name}: pushed {repo.get("pushed_at")} — https://github.com/{name}')
    lines += ['', '## Errors and access limits']
    for key, value in scan.items():
        if isinstance(value, dict) and value.get('error'):
            lines.append(f'- {key}: {value["error"]}')
    (folder / (filename + '.md')).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Public scan saved; {count("commits")} commits, {count("pulls?state=all")} PRs, {count("forks")} forks; {len(competitors)} search results (not all relevant).')

if __name__ == '__main__':
    main()
