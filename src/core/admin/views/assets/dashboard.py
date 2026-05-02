from sqladmin import BaseView, expose
from starlette.requests import Request
from starlette.responses import HTMLResponse


class DashboardView(BaseView):
    name = "Dashboard"
    identity = "dashboard"
    icon = "fa-solid fa-chart-line"

    @expose("/")
    async def index(self, request: Request) -> HTMLResponse:
        # Simple dashboard with some stats
        html = """
        <div class="container">
            <h1>IIB ATV Dashboard</h1>
            <div class="row">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Total Assets</h5>
                            <p class="card-text">Check Assets section for details</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Active Users</h5>
                            <p class="card-text">Check Users section</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Repairs</h5>
                            <p class="card-text">Ongoing repairs</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Transfers</h5>
                            <p class="card-text">Pending transfers</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        return HTMLResponse(content=html)
