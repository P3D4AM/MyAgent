"""Platform registry — everything the TaskEngine and CLI can drive."""

from platforms.base import BasePlatform
from platforms.instagram import Instagram
from platforms.twitter import Twitter
from platforms.telegram import Telegram
from platforms.facebook import Facebook
from platforms.linkedin import LinkedIn
from platforms.bale import Bale
from platforms.rubika import Rubika
from platforms.eitaa import Eitaa

PLATFORMS = {
    "instagram": Instagram,
    "twitter": Twitter,
    "telegram": Telegram,
    "facebook": Facebook,
    "linkedin": LinkedIn,
    "bale": Bale,
    "rubika": Rubika,
    "eitaa": Eitaa,
}

__all__ = [
    "BasePlatform", "PLATFORMS",
    "Instagram", "Twitter", "Telegram", "Facebook",
    "LinkedIn", "Bale", "Rubika", "Eitaa",
]
