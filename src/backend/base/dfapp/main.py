from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import nest_asyncio  # type: ignore
import socketio  # type: ignore
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from rich import print as rprint
from starlette.middleware.base import BaseHTTPMiddleware

from dfapp.api import router
from dfapp.initial_setup.setup import (
    create_or_update_starter_projects,
    initialize_super_user_if_needed,
    load_flows_from_directory,
)
from dfapp.interface.utils import setup_llm_caching
from dfapp.services.plugins.langfuse_plugin import LangfuseInstance
from dfapp.services.utils import initialize_services, teardown_services
from dfapp.utils.logger import configure


class JavaScriptMIMETypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(exc)
            raise exc
        if "files/" not in request.url.path and request.url.path.endswith(".js") and response.status_code == 200:
            response.headers["Content-Type"] = "text/javascript"
        return response


def get_lifespan(fix_migration=False, socketio_server=None, version=None):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nest_asyncio.apply()
        # Startup message
        if version:
            rprint(f"[bold green]Starting DataformerApp v{version}...[/bold green]")
        else:
            rprint("[bold green]Starting DataformerApp...[/bold green]")
        try:
            initialize_services(fix_migration=fix_migration, socketio_server=socketio_server)
            setup_llm_caching()
            LangfuseInstance.update()
            initialize_super_user_if_needed()
            create_or_update_starter_projects()
            load_flows_from_directory()
            yield
        except Exception as exc:
            if "dfapp migration --fix" not in str(exc):
                logger.error(exc)
            raise
        # Shutdown message
        rprint("[bold red]Shutting down DataformerApp...[/bold red]")
        teardown_services()

    return lifespan


def create_app():
    """Create the FastAPI app and include the router."""
    try:
        from dfapp.version import __version__  # type: ignore
    except ImportError:
        from importlib.metadata import version

        __version__ = version("dfapp-base")

    configure()
    socketio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*", logger=True)
    lifespan = get_lifespan(socketio_server=socketio_server, version=__version__)
    app = FastAPI(lifespan=lifespan, title="DataformerApp", version=__version__)
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(JavaScriptMIMETypeMiddleware)

    @app.middleware("http")
    async def flatten_query_string_lists(request: Request, call_next):
        flattened: list[tuple[str, str]] = []
        for key, value in request.query_params.multi_items():
            flattened.extend((key, entry) for entry in value.split(","))

        request.scope["query_string"] = urlencode(flattened, doseq=True).encode("utf-8")

        return await call_next(request)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(router)

    app = mount_socketio(app, socketio_server)

    return app


def mount_socketio(app: FastAPI, socketio_server: socketio.AsyncServer):
    app.mount("/sio", socketio.ASGIApp(socketio_server, socketio_path=""))
    return app


def setup_static_files(app: FastAPI, static_files_dir: Path):
    """
    Setup the static files directory.
    Args:
        app (FastAPI): FastAPI app.
        path (str): Path to the static files directory.
    """
    app.mount(
        "/",
        StaticFiles(directory=static_files_dir, html=True),
        name="static",
    )

    @app.exception_handler(404)
    async def custom_404_handler(request, __):
        path = static_files_dir / "index.html"

        if not path.exists():
            raise RuntimeError(f"File at path {path} does not exist.")
        return FileResponse(path)


def get_static_files_dir():
    """Get the static files directory relative to DataformerApp's main.py file."""
    frontend_path = Path(__file__).parent
    return frontend_path / "frontend"


def setup_app(static_files_dir: Optional[Path] = None, backend_only: bool = False) -> FastAPI:
    """Setup the FastAPI app."""
    # get the directory of the current file
    logger.info(f"Setting up app with static files directory {static_files_dir}")
    if not static_files_dir:
        static_files_dir = get_static_files_dir()

    if not backend_only and (not static_files_dir or not static_files_dir.exists()):
        raise RuntimeError(f"Static files directory {static_files_dir} does not exist.")
    app = create_app()
    if not backend_only and static_files_dir is not None:
        setup_static_files(app, static_files_dir)
    return app


if __name__ == "__main__":
    import uvicorn

    from dfapp.__main__ import get_number_of_workers

    configure()
    uvicorn.run(
        "dfapp.main:create_app",
        host="127.0.0.1",
        port=7860,
        workers=get_number_of_workers(),
        log_level="error",
        reload=True,
        loop="asyncio",
    )
