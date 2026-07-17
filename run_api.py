import os

os.environ.setdefault("GAIA_AUDIT_DB", "gaia_audit.db")
os.environ.setdefault("GAIA_JWT_SECRET", "change-me-in-production")

from core.api.api import create_app
from core.primordial.session import PrimordialSession

session = PrimordialSession()
session.boot()

app = create_app(session=session)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
