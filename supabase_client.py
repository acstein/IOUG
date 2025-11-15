# -*- coding: utf-8 -*-
"""
Created on Sat Nov 15 17:09:23 2025

@author: alice
"""

import os
from supabase import create_client

def get_supabase():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)
