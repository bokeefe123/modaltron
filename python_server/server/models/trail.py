"""
Trail class for avatar trails.
Port of server/model/Trail.js (inherits from BaseTrail)
"""
from typing import TYPE_CHECKING

from .base_trail import BaseTrail

if TYPE_CHECKING:
    from .avatar import Avatar


class Trail(BaseTrail):
    """
    Trail implementation for server-side avatars.
    """
    
    def __init__(self, avatar: 'Avatar'):
        super().__init__(avatar)

