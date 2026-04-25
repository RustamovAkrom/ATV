import re
import unicodedata


def slugify(value: str) -> str:
    """
    Простой slug:
    - lower
    - убирает спецсимволы
    - пробелы -> _
    """
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")

    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")

    return value
