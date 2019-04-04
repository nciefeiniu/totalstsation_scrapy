#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import hashlib


def get_md5(response: bytes):
    _m = hashlib.md5()
    _m.update(response)
    return _m.hexdigest()
