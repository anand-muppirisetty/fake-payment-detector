"""
Global rate limiter configuration using slowapi (Flask-Limiter style, async-friendly).
Applied per-route with @limiter.limit(...) decorators. IP-based by default.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
