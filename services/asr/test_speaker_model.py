import unittest,tempfile,json
from pathlib import Path
from speaker_model import select_speaker_model
class Tests(unittest.TestCase):
 def test_selection_persists_and_rejects_unknown_or_missing(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'data').mkdir();base=root/'models/speaker-campplus/model.onnx';base.parent.mkdir(parents=True);base.write_bytes(b'test-only');self.assertEqual(select_speaker_model(root)[0],'campplus')
   config=root/'data/speaker-model.json';config.write_text(json.dumps({'model':'campplus-advanced'}));self.assertRaises(FileNotFoundError,select_speaker_model,root);advanced=root/'models/speaker-campplus-advanced/model.onnx';advanced.parent.mkdir(parents=True);advanced.write_bytes(b'test-only');self.assertEqual(select_speaker_model(root),( 'campplus-advanced',advanced));self.assertEqual(select_speaker_model(Path(d))[0],'campplus-advanced');config.write_text(json.dumps({'model':'../../elsewhere'}));self.assertRaises(ValueError,select_speaker_model,root)
if __name__=='__main__':unittest.main()
