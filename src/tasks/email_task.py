from core.celery import celery_app
from core.email import send_email


@celery_app.task(bind=True, max_retries=3)
def send_password_reset_email_task(self, email: str, token: str):
    reset_link = f"http://localhost:5173/change-password?tokne={token}"

    try:
        if not email:
            raise ValueError("Email is required")

        body = f"""
        <h3>Password reset</h3>
        <a href="{reset_link}">{reset_link}</a>
        """

        send_email(
            to=email,
            subject="Password Reset",
            body=body,
        )

    except Exception as e:
        raise self.retry(exc=e, countdown=10) from e
