from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from api.factory import create_spider_router


class DummyRequest(BaseModel):
    page: int = 1


class DummyResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: list


class DummySpider:
    async def main(self, request):
        return ["a", "b"]


def _build_app() -> FastAPI:
    router = create_spider_router(
        spider=DummySpider(),
        path="/dummy",
        spider_name="dummy",
        request_model=DummyRequest,
        response_model=DummyResponse,
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/spider")
    return app


def test_factory_registers_post_route():
    schema = _build_app().openapi()
    path_item = schema["paths"]["/api/spider/dummy"]
    assert "post" in path_item


def test_factory_endpoint_returns_unified_body():
    client = TestClient(_build_app())
    resp = client.post("/api/spider/dummy", json={"page": 1})
    assert resp.status_code == 200
    assert resp.json() == {"code": 0, "message": "ok", "data": ["a", "b"]}
