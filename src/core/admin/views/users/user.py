from wtforms import PasswordField, Form
from wtforms.validators import DataRequired, EqualTo
from core.admin.base import BaseAdmin
from db.models.users.user import User
from core.security.passwords import hash_password


class UserAdmin(BaseAdmin, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    can_edit = True
    can_create = True
    can_delete = True

    async def scaffold_form(self, rules = None):
        form_class = await super().scaffold_form(rules)

        is_create = rules == self._form_create_rules

        if is_create:
            form_class.password = PasswordField(
                "Password",
                validators=[DataRequired()],
                render_kw={
                    "class": "form-control",
                    "placeholder": "Enter password",
                }
            )

            form_class.password_confirm = PasswordField(
                "Confirm Password",
                validators=[
                    DataRequired(),
                    EqualTo("password", message="Passwords must match"),
                ],
                render_kw={
                    "class": "form-control",
                    "placeholder": "Enter password",
                }
            )

        return form_class

    form_create_rules = [
        "login",
        "email",
        "phone",
        "role",
        "status",
        "password",
        "password_confirm",
    ]

    form_edit_rules = [
        "login",
        "email",
        "phone",
        "first_name",
        "last_name",
        "status",
        "role",
        "region",
        "service",
    ]

    async def on_model_change(self, data, model, is_created, request):
        password = data.get("password")

        if is_created and not password:
            raise ValueError("Password is required")

        if password:
            model.password_hash = hash_password(password)

        return await super().on_model_change(data, model, is_created, request)

    column_list = [
        "id",
        "login",
        "email",
        "phone",
        "full_name",
        "status",
        "role",
        "region",
        "service",
        "created_at",
        "updated_at",
    ]

    column_searchable_list = [
        "login",
        "email",
        "first_name",
        "last_name",
    ]

    column_sortable_list = [
        "created_at",
        "login",
        "email",
    ]

    column_formatters = {
        "role": lambda m, _: m.role.name if m.role else None,
        "region": lambda m, _: m.region.name if m.region else None,
        "service": lambda m, _: m.service.name if m.service else None,
    }

    column_formatters_detail = {
        "permissions": lambda m, _: ", ".join(m.permissions),
    }

    form_excluded_columns = [
        "password_hash",
        "owned_assets",
        "direct_permissions",
    ]
