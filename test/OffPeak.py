
from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel

opm = OffPeakHoursModel()

is_off_peak = opm.is_off_peak_now()

print(f"Is off peak now: {is_off_peak}")