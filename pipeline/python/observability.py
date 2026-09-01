"""Pure modern observational coverage calculations; never hazard metrics."""
from __future__ import annotations
from datetime import datetime,timedelta
def summary(records, latest, as_of, period_days):
    start=as_of-timedelta(days=period_days); active=[r for r in records if datetime.fromisoformat(r["observed_at"].replace("Z","+00:00"))>=start]
    def n(family,state=None):return sum(r.get("measurement_family")==family and (state is None or r.get("observation_state")==state) for r in active)
    return {"period_days":period_days,"total_acquisitions":len(active),"optical_acquisitions":n("optical"),"usable_optical":sum(r.get("measurement_family")=="optical" and r.get("observation_state") in {"processed","reviewed","published"} for r in active),"rejected_optical":n("optical","rejected"),"sar_acquisitions":n("sar"),"usable_sar":sum(r.get("measurement_family")=="sar" and r.get("observation_state") in {"processed","reviewed","published"} for r in active),"rejected_sar":n("sar","rejected"),"latest_published_observation":latest,"days_since_defensible_observation":None if not latest else max(0,int((as_of-datetime.fromisoformat(latest["observed_at"].replace("Z","+00:00"))).total_seconds()//86400))}
