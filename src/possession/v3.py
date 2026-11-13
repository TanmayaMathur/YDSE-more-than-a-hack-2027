"""Separate V3 inference: frozen V2 team model plus externally trained dead-head blend."""
import json
from pathlib import Path
from .data import load_tracking
from .official import ROOT,BLOCKS,FPS,PITCH,load_tags
from .live_dead_experiment import prepare,infer_prepared

def load_model(config):
    path=Path(config['dead_model_path'])
    if not path.is_absolute():path=ROOT/path
    model=json.loads(path.read_text(encoding='utf-8'))
    if model.get('training_matches')!=['J03WOH'] or not model.get('no_competition_training'):
        raise ValueError('Unexpected learned-model provenance')
    return model

def infer(tracking,events,config,model=None,blocks=BLOCKS,fps=FPS,pitch=PITCH,return_diagnostics=False):
    model=model or load_model(config)
    chunks=prepare(tracking,events,config,blocks,fps,pitch)
    return infer_prepared(chunks,len(tracking.ball),config,model,config['dead_head_mode'],fps,return_diagnostics)

def run(data_dir,config):
    return infer(load_tracking(data_dir),load_tags(data_dir=str(data_dir)),config)
