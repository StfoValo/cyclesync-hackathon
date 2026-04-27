import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'cycle_sync_app'))
from models.oem_models.fleet_model import FleetModel

model = FleetModel()
print("Simulating fleet...")
model.simulate_regional_fleet(2)

print("Fetching analytics...")
res = model.get_bev_regional_analytics(2)
print(f'Total Regions: {len(res)}')
for r in res:
    print(f"{r['region_name']}: total_bevs={r['total_bevs']}, 0-3={r['cohorts']['0-3_months']}, 3-6={r['cohorts']['3-6_months']}, 6-12={r['cohorts']['6-12_months']}, safe={r['cohorts']['safe']}")
