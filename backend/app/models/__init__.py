"""Import all models here so Base.metadata is aware of them for create_all()/Alembic autogenerate."""
from app.models.user import User  # noqa: F401
from app.models.analysis import Analysis  # noqa: F401
from app.models.system_log import SystemLog  # noqa: F401
