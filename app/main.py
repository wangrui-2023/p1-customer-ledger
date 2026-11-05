"""P1 客户台账应用的入口。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import db

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="P1 客户台账", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def validate_form(name: str, phone: str) -> tuple[str, str, list[str]]:
    clean_name = name.strip()
    clean_phone = phone.strip()
    errors: list[str] = []
    if not clean_name:
        errors.append("姓名必填")
    if clean_phone and not clean_phone.isdigit():
        errors.append("手机号只能包含数字")
    return clean_name, clean_phone, errors


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/customers", status_code=303)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/customers")
def customers(request: Request, q: str = Query(default="")):
    keyword = q.strip()
    rows = db.list_customers(keyword)
    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={"customers": rows, "q": keyword},
    )


@app.get("/customers/new")
def new_customer(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="customer_new.html",
        context={"errors": [], "form": {}},
    )


@app.post("/customers")
def create_customer(
    request: Request,
    name: str = Form(default=""),
    phone: str = Form(default=""),
    company: str = Form(default=""),
    note: str = Form(default=""),
):
    clean_name, clean_phone, errors = validate_form(name, phone)
    form_data = {
        "name": name,
        "phone": phone,
        "company": company,
        "note": note,
    }

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="customer_new.html",
            context={"errors": errors, "form": form_data},
            status_code=422,
        )

    db.create_customer(
        name=clean_name,
        phone=clean_phone,
        company=company.strip(),
        note=note.strip(),
    )
    return RedirectResponse(url="/customers", status_code=303)
