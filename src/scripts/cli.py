import typer

from scripts.runner import run

app = typer.Typer(help="System CLI")


@app.command()
def bootstrap():
    """Init RBAC"""
    from scripts.bootstrap.rbac import seed_rbac

    run(seed_rbac)


@app.command()
def create_superadmin():
    """Create superadmin"""
    from scripts.users.create_superadmin import create_superadmin

    run(create_superadmin)


@app.command()
def cleanup_tokens():
    """Cleanup expired tokens"""
    from scripts.cleanup.tokens import cleanup_expired_tokens

    run(cleanup_expired_tokens)


@app.command()
def init():
    """Full init"""
    from scripts.bootstrap.rbac import seed_rbac
    from scripts.users.create_superadmin import create_superadmin

    run(seed_rbac)
    run(create_superadmin)


if __name__ == "__main__":
    app()
