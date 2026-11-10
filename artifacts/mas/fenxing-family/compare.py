"""Run the same core tests in isolated processes against explicit frozen files."""
from pathlib import Path
import subprocess
import sys
import json
from hashlib import sha256
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
results={}
for name in ('baseline','python_pro'):
    source=out/name/'fenxing.py'
    code='''import importlib.util, sys, pytest
path=sys.argv[1]
spec=importlib.util.spec_from_file_location('chanlab.algo.fenxing',path)
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
print('IMPORTED:',module.__file__,flush=True)
raise SystemExit(pytest.main(['tests/test_fenxing.py','-q']))
'''
    run=subprocess.run([sys.executable,'-c',code,str(source)],cwd=root,capture_output=True,text=True)
    (out/name/'final-tests.txt').write_text(run.stdout+run.stderr)
    results[name]={'returncode':run.returncode,'source':str(source.relative_to(root)),'sha256':sha256(source.read_bytes()).hexdigest()}
(out/'comparison.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
