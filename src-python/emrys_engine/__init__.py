"""
emrys_engine — GAIA-OS Emrys L2 Vibronic Bridge FastAPI Router

Exposes the EmrysCycle engine from src/crystals/emryscycle.py
as a set of REST endpoints under /api/emrys/.

Registration in main.py:
    from emrys_engine.router import emrys_router, init_emrys_engine
    init_emrys_engine()
    app.include_router(emrys_router, prefix="/api/emrys", tags=["Emrys"])

Per C164: the router is the digital bridge. The crystals are real.
Per C166.A4: physics and metaphysics are the same layer.
"""
