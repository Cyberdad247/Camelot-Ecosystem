# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from datetime import datetime


def get_current_timestamp(format_string: str = "%Y%m%d%H%M%S") -> str:
    """
    Returns the current timestamp in the given format.
    """
    return datetime.now().strftime(format_string)
