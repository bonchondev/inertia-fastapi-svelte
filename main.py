import os
from typing import Annotated, Dict
from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from inertia import (
    InertiaResponse,
    Inertia,
    inertia_dependency_factory,
    inertia_version_conflict_exception_handler,
    inertia_request_validation_exception_handler,
    InertiaVersionConflictException,
    InertiaConfig,
)

template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret_key")
app.add_exception_handler(
    InertiaVersionConflictException,
    inertia_version_conflict_exception_handler,  # type: ignore[arg-type]
)
app.add_exception_handler(
    RequestValidationError,
    inertia_request_validation_exception_handler,  # type: ignore[arg-type]
)

# manifest_json = os.path.join(
#     os.path.dirname(__file__), "views", "dist", "manifest.json"
# )

inertia_config = InertiaConfig(
    templates=templates,
    # manifest_json_path=manifest_json,
    environment="development",
    use_flash_messages=True,
    use_flash_errors=True,
    entrypoint_filename="main.js",
    assets_prefix="/src",
)

InertiaDep = Annotated[Inertia, Depends(inertia_dependency_factory(inertia_config))]


svelte_dir = (
    os.path.join(os.path.dirname(__file__), "views", "dist")
    if inertia_config.environment != "development"
    else os.path.join(os.path.dirname(__file__), "views", "src")
)

app.mount("/src", StaticFiles(directory=svelte_dir), name="src")
app.mount(
    "/assets", StaticFiles(directory=os.path.join(svelte_dir, "assets")), name="assets"
)


@app.get("/", response_model=None)
async def index(inertia: InertiaDep) -> InertiaResponse:
    props = {
        "message": "hello from index",
    }
    return await inertia.render("Index", props)


@app.get("/about", response_model=None)
async def about(inertia: InertiaDep) -> InertiaResponse:
    props = {
        "amount": "$100",
    }
    return await inertia.render("About", props)


@app.post("/data", response_model=None)
async def data() -> Dict[str, str]:
    return {"dollars": "$7,000"}
