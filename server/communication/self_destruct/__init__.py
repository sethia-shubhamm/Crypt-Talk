"""
Self Destruct Timer Module for Crypt-Talk
Handles automatic message deletion based on user-set timers
"""

from .timer_handler import create_self_destruct_routes, add_self_destruct_to_message

__all__ = ['create_self_destruct_routes', 'add_self_destruct_to_message']