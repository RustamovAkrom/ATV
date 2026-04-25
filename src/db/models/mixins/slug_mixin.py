from sqlalchemy.orm import validates
from utils.slug import slugify


class SlugMixin:
    code: str

    @validates("name")
    def _generate_slug(self, key, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")

        value = value.strip()

        if not getattr(self, "code", None):
            self.code = slugify(value)
        return value
