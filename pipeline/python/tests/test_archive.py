import unittest
from datetime import datetime,timezone
from archive_policy import scene_state,select_yearly_candidates,season_window
from landsat import SENSORS,slc_off_reasons
from observability import summary
from spatial_compare import compare_geojson

class ArchiveTest(unittest.TestCase):
 def test_landsat_specs_and_slc_off(self):
  self.assertEqual(SENSORS['LANDSAT/LT05/C02/T1_L2']['green'],'SR_B2');self.assertIn('LANDSAT_7_SLC_OFF',slc_off_reasons('Landsat 7',datetime(2004,1,1,tzinfo=timezone.utc)))
 def test_gap_not_forced(self):
  self.assertEqual(scene_state(available=False,rejection_reasons=[]),('unavailable',False));self.assertEqual(select_yearly_candidates([{'available':True,'usable':False,'observed_at':'2000-01-01'}]),[]);self.assertEqual(season_window(2020,'10-01','02-01'),('2020-10-01','2021-02-01'))
 def test_landsat_sensor_specific_bands(self):
  self.assertEqual(SENSORS['LANDSAT/LC08/C02/T1_L2']['green'],'SR_B3');self.assertEqual(SENSORS['LANDSAT/LT05/C02/T1_L2']['green'],'SR_B2')
 def test_observability(self):
  now=datetime(2026,8,28,tzinfo=timezone.utc);r=[{'observed_at':'2026-08-20T00:00:00Z','measurement_family':'optical','observation_state':'rejected'},{'observed_at':'2026-08-21T00:00:00Z','measurement_family':'sar','observation_state':'processed'}];self.assertEqual(summary(r,None,now,30)['rejected_optical'],1)
  self.assertIsNone(summary(r,None,now,30)['latest_published_observation'])
 def test_polygon_iou(self):
  a={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Polygon','coordinates':[[[0,0],[2,0],[2,2],[0,2],[0,0]]]}}]};b={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Polygon','coordinates':[[[1,0],[3,0],[3,2],[1,2],[1,0]]]}}]};self.assertAlmostEqual(compare_geojson(a,b)['iou'],1/3)
  self.assertAlmostEqual(compare_geojson(a,b)['optical_omission_fraction'],.5)
