import smtplib

import pytest

from core import email


def test_send_email_rejects_empty_recipient():
    with pytest.raises(ValueError, match="Recipient email is empty"):
        email.send_email("", "subject", "body")


def test_send_email_rejects_invalid_recipient():
    with pytest.raises(ValueError, match="Invalid email address"):
        email.send_email("invalid-address", "subject", "body")


def test_send_email_success(monkeypatch):
    class _Server:
        def ehlo(self):
            return None

        def starttls(self):
            return None

        def login(self, _user, _password):
            return None

        def send_message(self, _msg):
            return {}

    class _SMTPContext:
        def __enter__(self):
            return _Server()

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(email.smtplib, "SMTP", lambda *_args, **_kwargs: _SMTPContext())

    email.send_email("user@test.local", "subject", "<b>hello</b>")


def test_send_email_maps_recipients_refused(monkeypatch):
    class _SMTPContext:
        def __enter__(self):
            raise smtplib.SMTPRecipientsRefused({"user@test.local": (550, b"bad")})

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(email.smtplib, "SMTP", lambda *_args, **_kwargs: _SMTPContext())

    with pytest.raises(Exception, match="Recipients refused"):
        email.send_email("user@test.local", "subject", "body")


def test_send_email_maps_authentication_error(monkeypatch):
    class _SMTPContext:
        def __enter__(self):
            raise smtplib.SMTPAuthenticationError(535, b"auth failed")

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(email.smtplib, "SMTP", lambda *_args, **_kwargs: _SMTPContext())

    with pytest.raises(Exception, match="SMTP authentication failed"):
        email.send_email("user@test.local", "subject", "body")


def test_send_email_maps_smtp_exception(monkeypatch):
    class _SMTPContext:
        def __enter__(self):
            raise smtplib.SMTPException("network down")

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(email.smtplib, "SMTP", lambda *_args, **_kwargs: _SMTPContext())

    with pytest.raises(Exception, match="SMTP error: network down"):
        email.send_email("user@test.local", "subject", "body")


def test_send_email_raises_for_rejected_result(monkeypatch):
    class _Server:
        def ehlo(self):
            return None

        def starttls(self):
            return None

        def login(self, _user, _password):
            return None

        def send_message(self, _msg):
            return {"user@test.local": (550, b"bad")}

    class _SMTPContext:
        def __enter__(self):
            return _Server()

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(email.smtplib, "SMTP", lambda *_args, **_kwargs: _SMTPContext())

    with pytest.raises(Exception, match="SMTP rejected recipients"):
        email.send_email("user@test.local", "subject", "body")
