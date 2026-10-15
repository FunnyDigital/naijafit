from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import APP_VERSION, FRONTEND_DIST, SITE_TITLE
from app.routes import (
    admin,
    dashboard,
    exercises,
    foods,
    logs,
    meta,
    options,
    plan,
    profile,
)
from app.seed import seed_database

seed_database()

app = FastAPI(
    title=f"{SITE_TITLE} API",
    description="Home workouts and Nigerian meal plans — profile, plans, logs.",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (meta, options, profile, foods, exercises, plan, logs, dashboard, admin):
    app.include_router(module.router)


@app.get("/api")
def api_root():
    return {"message": f"{SITE_TITLE} API", "version": APP_VERSION, "docs": "/docs"}


class SpaStaticFiles(StaticFiles):
    """Serves the built interface and falls back to index.html for client-side routes.

    Anything under /api or /media must stay a normal 404 so the interface never
    receives an HTML page where it expected JSON.
    """

    RESERVED = ("/api", "/docs", "/redoc", "/openapi.json")

    async def get_response(self, path, scope):
        request_path = scope.get("path", "")
        reserved = (
            request_path == "/api"
            or request_path.startswith(
                tuple(prefix + "/" for prefix in self.RESERVED)
            )
            or request_path in self.RESERVED
        )

        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and not reserved:
                return await super().get_response("index.html", scope)
            raise

        if response.status_code == 404 and not reserved:
            return await super().get_response("index.html", scope)
        return response


if FRONTEND_DIST.is_dir():
    app.mount("/", SpaStaticFiles(directory=str(FRONTEND_DIST), html=True), name="spa")
else:

    @app.get("/")
    def root():
        return {
            "message": f"{SITE_TITLE} API",
            "version": APP_VERSION,
            "docs": "/docs",
            "hint": "Interface build not found — run `npm run build` in frontend/, or use the Vite dev server.",
        }
