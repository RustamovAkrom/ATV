# src/scripts/cli.py

import sys

from scripts.db import run
from scripts.seed_permissions import seed_permissions
from scripts.seed_roles import seed_roles
from scripts.create_admin import create_admin


COMMANDS = {
    "permissions": seed_permissions,
    "roles": seed_roles,
    "admin": create_admin,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: cli [permissions|roles|admin]")
        exit(1)

    cmd = sys.argv[1]

    if cmd not in COMMANDS:
        print("Unknown command")
        exit(1)

    run(COMMANDS[cmd])


if __name__ == "__main__":
    main()
