import unittest
from lifecycle import can_transition
from review_queue import ranked_candidates

class ReviewQueueTest(unittest.TestCase):
 def test_ranks_representative_candidates_without_publishing(self):
  records=[{"observation_state":"processed","value":value,"observed_at":f"2021-11-0{i}T00:00:00Z","measurement_family":"optical","source":"Sentinel-2","provenance":{"sensor":"Sentinel-2"},"qa":{"lake_envelope_valid_fraction":coverage}} for i,(value,coverage) in enumerate([(1.0,.9),(1.1,.99),(1.5,1.0)],1)]
  ranked=ranked_candidates(records,2)
  best=next(item for item in ranked if item["review_rank"]==1)
  self.assertEqual(best["value"],1.1);self.assertTrue(best["review_recommended"]);self.assertEqual(max(item["review_rank"] for item in ranked),3)
 def test_human_rejection_is_valid_from_processed_only(self):
  self.assertTrue(can_transition("processed","rejected",[]));self.assertFalse(can_transition("reviewed","rejected",[]))
