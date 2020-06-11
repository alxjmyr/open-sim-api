from fastapi import FastAPI

from src.api import core, discrete_event

app: FastAPI = FastAPI(
        title="Open Sim",
        description="Open Sim provides simulation as a service in a composeable HTTP API",
        version="0.1.0beta",
        docs_url=None,
        redoc_url="/documentation"
)

app.include_router(core.router, tags=["core"])
app.include_router(discrete_event.router, tags=["Discrete Event Simulation"], prefix="/discrete-event")

if __name__ == '__main__':
    import uvicorn  # type: ignore # pragma: no cover

    uvicorn.run(app=app, host="localhost", port=8000)  # pragma: no cover
