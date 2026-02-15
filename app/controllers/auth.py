from litestar import Controller, get, post, Request
import httpx
from litestar.response import Template, Redirect

API_URL = "http://localhost:8282"  # сервис A (REST API)


class AuthController(Controller):
    route_handlers = []

    @get("/login", name="login")
    async def login_page(self) -> Template:
        return Template("auth/login.html")

    @post("/login")
    async def login_submit(self, request: Request) -> Template | Redirect:
        form = await request.form()
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{API_URL}/auth", json={
                "username": form.get("username"),
                "password": form.get("password")
            })
        if resp.status_code == 201:
            return Redirect("/dashboard")  # редирект после успешного логина
        else:
            return Template("auth/login.html", context={"error": resp.json()})

    @get("/register", name="register")
    async def register_page(self) -> Template:
        return Template("auth/registration.html")

    @post("/register")
    async def register_submit(self, request: Request) -> Template | Redirect:
        form = await request.form()
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{API_URL}/auth/registration", json={
                "username": form.get("username"),
                "email": form.get("email"),
                "password": form.get("password")
            })
        if resp.status_code == 201:
            return Redirect("/login")
        else:
            return Template("auth/registration.html", context={"error": resp.json()})

    @get("/change-password", name="change_password_page")
    async def change_password_page(self) -> Template:
        return Template("auth/change_password.html")

    @post("/change-password")
    async def change_password_submit(self, request: Request) -> Template | Redirect:
        form = await request.form()
        token = form.get("change_password_token")  # из формы
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{API_URL}/user/change-password/{token}", json={
                "password": form.get("password")
            })
        if resp.status_code == 200:
            return Redirect("/login")
        else:
            return Template("auth/change_password.html", context={"error": resp.json()})
