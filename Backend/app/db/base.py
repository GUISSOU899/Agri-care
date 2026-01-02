# Backend/app/db/base.py
# ⚠️ Important: cet import force l’enregistrement de tous les modèles dans Base.metadata
from app.db.base_class import Base  # noqa

from app.models.region import Region  # noqa
from app.models.crop import Crop  # noqa
from app.models.weather import WeatherDaily  # noqa
from app.models.forecast import Forecast  # noqa
from app.models.alert import Alert  # noqa
from app.models.yield_data import YieldHistory  # noqa
from app.models.user import User  # noqa
from app.models.climatology import ClimatologyDaily  # noqa
from app.models.seasonal import YieldObserved, NDVITimeseries, SeasonCalendar, AquaCropSim  # noqa
