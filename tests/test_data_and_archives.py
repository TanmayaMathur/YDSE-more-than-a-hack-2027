import json
from pathlib import Path
import stat
import zipfile
import numpy as np
import pytest
from prepare_data import extract_safe
from possession.data import parse_tracking
from possession.official import BLOCKS, N_FRAMES
from generate_submission import write_csv
import possession_metrics as pm

@pytest.mark.parametrize('name', ['../escape.txt', '/absolute', 'C:/escape', 'a/../../bad', 'CON.txt', 'a./file'])
def test_unsafe_archive_rejected(tmp_path, name):
    z = tmp_path / 'bad.zip'
    with zipfile.ZipFile(z, 'w') as f:
        f.writestr(name, 'payload')
    with pytest.raises(ValueError):
        extract_safe(z, tmp_path / 'out')
    assert not (tmp_path / 'out').exists()

def test_collision_isolation_no_overwrite(tmp_path):
    for i, content in enumerate(['one', 'two']):
        z = tmp_path / f'{i}.zip'
        with zipfile.ZipFile(z, 'w') as f:
            f.writestr('tracking.xml', content)
        extract_safe(z, tmp_path / str(i))
        with pytest.raises(FileExistsError):
            extract_safe(z, tmp_path / str(i))
    assert (tmp_path/'0'/'tracking.xml').read_text() == 'one'
    assert (tmp_path/'1'/'tracking.xml').read_text() == 'two'

def test_duplicate_case_and_symlink_rejected(tmp_path):
    z = tmp_path/'duplicate.zip'
    with zipfile.ZipFile(z, 'w') as f:
        f.writestr('A.txt', 'a')
        f.writestr('a.txt', 'b')
    with pytest.raises(ValueError):
        extract_safe(z, tmp_path/'out')
    with zipfile.ZipFile(z, 'w') as f:
        info = zipfile.ZipInfo('link')
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        f.writestr(info, '../outside')
    with pytest.raises(ValueError):
        extract_safe(z, tmp_path/'out')

def test_parser_index_nan_and_strictness(tmp_path):
    path = tmp_path/'tiny.txt'
    path.write_text('1:0.1,0.2,1;0.3,0.4,2:0.2,0.2,1\n2:NaN,NaN,NaN;0.4,0.5,2:NaN,NaN,NaN\n')
    p, b = parse_tracking(path, 2, 2)
    assert p.shape == (2,2,3) and b[0,0] == pytest.approx(.2)
    assert np.isnan(b[1]).all()
    path.write_text('2:0,0,0;0,0,0:0,0,0\n')
    with pytest.raises(ValueError, match='alignment'):
        parse_tracking(path, 1, 2)

def test_official_halves_and_csv_reproducibility(tmp_path):
    labels = np.full(N_FRAMES, 'X')
    for a,b in BLOCKS:
        labels[a:b] = 'D'
    assert np.sum(labels != 'X') == 158857
    p, q = tmp_path/'one.csv', tmp_path/'two.csv'
    write_csv(p, labels)
    write_csv(q, labels)
    assert p.read_bytes() == q.read_bytes()
    table = pm.read_label_csv(p)
    assert list(table.columns) == ['frame','label']
    assert pm.validate_submission(table, N_FRAMES) is None
    table.loc[2,'frame'] = 1
    assert pm.validate_submission(table, N_FRAMES) is not None

def test_team_mapping_uses_metadata_team_order(tmp_path):
    from possession.official import team_of_each_track
    path = tmp_path/'metadata.xml'
    path.write_text('<root><Team id="home"/><Team id="away"/><Player teamId="away"/><Player teamId="home"/></root>')
    assert team_of_each_track(path).tolist() == [1,0]

def test_corrupt_archive_and_expansion_limit(tmp_path):
    from prepare_data import safe_members
    z=tmp_path/'broken.zip';z.write_bytes(b'broken')
    with pytest.raises(zipfile.BadZipFile):
        extract_safe(z,tmp_path/'out')
    with zipfile.ZipFile(z,'w') as f:
        f.writestr('a.txt','12345')
    with zipfile.ZipFile(z) as f:
        with pytest.raises(ValueError,match='expansion'):
            safe_members(f,limit=4)
