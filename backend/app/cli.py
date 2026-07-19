"""Small admin tasks.

    python -m app.cli create-admin
    python -m app.cli list-admins
    python -m app.cli reset-password
    python -m app.cli deactivate-admin

The password is always typed at a prompt, never passed as an argument — command
line arguments end up in shell history and in `ps` output for any other user on
the machine to read.
"""

import getpass
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.admin import AdminUser

MIN_PASSWORD_LENGTH = 12


def _session() -> Session:
    return Session(create_engine(settings.sync_database_url, future=True))


def _prompt_password(confirm: bool = True) -> str:
    while True:
        password = getpass.getpass("Password (typing is hidden): ")

        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"  Too short — use at least {MIN_PASSWORD_LENGTH} characters.\n")
            continue
        if password.lower() in {"password", "manero", "admin", "12345678"}:
            print("  Too easy to guess. Pick something else.\n")
            continue

        if not confirm:
            return password

        if password != getpass.getpass("Confirm password: "):
            print("  Those did not match. Try again.\n")
            continue

        return password


def create_admin() -> int:
    email = input("Email: ").strip().lower()
    if not email or "@" not in email:
        print("That does not look like an email address.")
        return 1

    name = input("Name (optional): ").strip()

    with _session() as session:
        if session.scalar(select(AdminUser).where(AdminUser.email == email)):
            print(f"An admin with {email} already exists. Use reset-password.")
            return 1

        password = _prompt_password()
        session.add(
            AdminUser(email=email, name=name, password_hash=hash_password(password))
        )
        session.commit()

    print(f"\nAdmin created: {email}")
    print("Sign in at http://localhost:5173/admin/login")
    return 0


def list_admins() -> int:
    with _session() as session:
        admins = session.scalars(select(AdminUser).order_by(AdminUser.id)).all()

    if not admins:
        print("No admin accounts yet. Create one with: python -m app.cli create-admin")
        return 0

    print(f"{'ID':<4} {'EMAIL':<34} {'ACTIVE':<7} LAST LOGIN")
    for a in admins:
        last = a.last_login_at.strftime("%Y-%m-%d %H:%M") if a.last_login_at else "never"
        print(f"{a.id:<4} {a.email:<34} {'yes' if a.is_active else 'no':<7} {last}")
    return 0


def reset_password() -> int:
    email = input("Email of the account to reset: ").strip().lower()

    with _session() as session:
        admin = session.scalar(select(AdminUser).where(AdminUser.email == email))
        if admin is None:
            print(f"No admin found with {email}.")
            return 1

        admin.password_hash = hash_password(_prompt_password())
        session.commit()

    print(f"\nPassword updated for {email}.")
    return 0


def deactivate_admin() -> int:
    email = input("Email of the account to deactivate: ").strip().lower()

    with _session() as session:
        admin = session.scalar(select(AdminUser).where(AdminUser.email == email))
        if admin is None:
            print(f"No admin found with {email}.")
            return 1

        active_count = len(
            session.scalars(
                select(AdminUser).where(AdminUser.is_active.is_(True))
            ).all()
        )
        if admin.is_active and active_count <= 1:
            print("That is the only active admin — you would lock yourself out.")
            return 1

        admin.is_active = False
        session.commit()

    print(f"{email} can no longer sign in. Their records are kept.")
    return 0


COMMANDS = {
    "create-admin": create_admin,
    "list-admins": list_admins,
    "reset-password": reset_password,
    "deactivate-admin": deactivate_admin,
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: python -m app.cli <command>\n\nCommands:")
        for name in COMMANDS:
            print(f"  {name}")
        return 1
    return COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
