import unittest,numpy as np
from speaker_gate import SpeakerGate
class Stream:
 def accept_waveform(self,sr,a):self.audio=a
 def input_finished(self):pass
class Extractor:
 def create_stream(self):return Stream()
 def is_ready(self,s):return True
 def compute(self,s):return [1,0] if s.audio[0]>0 else [0,1]
class Tests(unittest.TestCase):
 def test_gate(self):
  now=[0];g=SpeakerGate(Extractor(),clock=lambda:now[0]);a=np.full(32000,.04,dtype=np.float32);t=g.enroll(a,'office')
  self.assertTrue(g.verify(a,t,'office')['accepted']);self.assertFalse(g.verify(-a,t,'office')['accepted']);self.assertFalse(g.verify(a,t,'restaurant')['accepted']);self.assertFalse(g.verify(a[:3000],t,'office')['accepted']);g.release(t,'restaurant');self.assertTrue(g.verify(a,t,'office')['accepted']);g.release(t,'office');self.assertFalse(g.verify(a,t,'office')['accepted']);t=g.enroll(a,'office');now[0]=601;self.assertFalse(g.verify(a,t,'office')['accepted']);self.assertEqual(len(g.sessions),0)
 def test_matching_start_does_not_authorize_other_voice_later(self):
  g=SpeakerGate(Extractor());a=np.full(32000,.04,dtype=np.float32);t=g.enroll(a,'office')
  mixed=np.concatenate([a,-a]);self.assertTrue(g.verify(mixed,t,'office')['accepted']);result=g.verify(mixed,t,'office',strict=True)
  self.assertEqual(result['score'],1);self.assertFalse(result['accepted']);self.assertEqual(result['lowestWindowScore'],0)
  self.assertTrue(g.verify(np.concatenate([a,a]),t,'office')['accepted'])
 def test_short_window_tolerance_keeps_whole_sentence_threshold(self):
  class Variation(Extractor):
   def compute(self,s):
    if s.audio[0]<.045:return [1,0]
    score=.62 if len(s.audio)<=32000 else .71
    return [score,(1-score*score)**.5]
  g=SpeakerGate(Variation());a=np.full(32000,.04,dtype=np.float32);t=g.enroll(a,'office');result=g.verify(np.full(64000,.05,dtype=np.float32),t,'office',strict=True)
  self.assertTrue(result['accepted']);self.assertAlmostEqual(result['lowestWindowScore'],.62);self.assertEqual(result['threshold'],.65);self.assertEqual(result['windowThreshold'],.5)
 def test_conversation_mode_does_not_veto_strong_whole_sentence(self):
  class Tail(Extractor):
   def compute(self,s):
    if s.audio[0]<.045:return [1,0]
    score=.9089 if len(s.audio)>32000 else .0801
    return [score,(1-score*score)**.5]
  g=SpeakerGate(Tail());t=g.enroll(np.full(32000,.04,dtype=np.float32),'office');a=np.full(64000,.05,dtype=np.float32)
  self.assertTrue(g.verify(a,t,'office')['accepted']);self.assertFalse(g.verify(a,t,'office',strict=True)['accepted'])
 def test_explicit_update_only_and_bounded_references(self):
  g=SpeakerGate(Extractor());a=np.full(32000,.04,dtype=np.float32);t=g.enroll(a,'office');self.assertFalse(g.verify(-a,t,'office')['accepted']);self.assertEqual(len(g.sessions[t][1]),1)
  self.assertRaises(ValueError,g.update,-a,t,'restaurant');g.update(-a,t,'office');self.assertTrue(g.verify(-a,t,'office')['accepted']);self.assertFalse(g.verify(a,t,'office')['accepted']);self.assertEqual(len(g.sessions[t][1]),1)
  for _ in range(4):g.update(a,t,'office')
  self.assertEqual(len(g.sessions[t][1]),2);g.release(t,'office');self.assertRaises(ValueError,g.update,a,t,'office')
class ConfirmedBankTests(unittest.TestCase):
 def test_confirmed_variants_bound_expiry_and_no_implicit_learning(self):
  class Variants(Extractor):
   def compute(self,s):
    v=np.zeros(6);v[min(5,int(round(float(s.audio[0])*100)))]=1;return v
  now=[0];g=SpeakerGate(Variants(),clock=lambda:now[0]);audio=lambda n:np.full(32000,n/100,dtype=np.float32)
  t=g.enroll(audio(1),'office');expiry=g.sessions[t][2]
  self.assertTrue(g.update(audio(2),t,'office')['referenceReplaced'])
  self.assertFalse(g.verify(audio(1),t,'office')['accepted'])
  self.assertFalse(g.update(audio(3),t,'office')['referenceReplaced'])
  self.assertTrue(g.verify(audio(2),t,'office')['accepted']);self.assertTrue(g.verify(audio(3),t,'office')['accepted'])
  self.assertFalse(g.verify(audio(4),t,'office')['accepted']);self.assertEqual(len(g.sessions[t][1]),2)
  g.update(audio(3),t,'office');self.assertEqual(len(g.sessions[t][1]),2)
  g.update(audio(4),t,'office');g.update(audio(5),t,'office');self.assertEqual(len(g.sessions[t][1]),3)
  self.assertFalse(g.verify(audio(2),t,'office')['accepted']);self.assertEqual(g.sessions[t][2],expiry)
  now[0]=601;self.assertFalse(g.verify(audio(5),t,'office')['accepted']);self.assertNotIn(t,g.confirmed)
if __name__=='__main__':unittest.main()
