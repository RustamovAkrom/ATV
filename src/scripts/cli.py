# src/scripts/cli.py

import typer
from scripts.runner import run

app = typer.Typer()


@app.command()
def bootstrap():
    """🔥 Initialize system (roles + permissions)"""
    from scripts.bootstrap.roles import seed_roles_permissions
    run(seed_roles_permissions)


@app.command()
def create_superadmin():
    """🔥 Create superadmin"""
    from scripts.users.create_superadmin import create_superadmin
    run(create_superadmin)


if __name__ == "__main__":
    app()
