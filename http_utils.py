# -*- coding: utf-8 -*-
"""
非公式サイトへのアクセス時、一時的なアクセス制限(429など)に遭遇した場合に
間隔を空けてリトライする共通処理。
"""
import time

import requests


def get_with_retry(url, headers, timeout=20, max_retries=3, backoff_seconds=15):
    """
    max_retries回まで、失敗するたびに backoff_seconds * (試行回数) 待ってから再試行する。
    全て失敗した場合は最後の例外を送出する。
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(backoff_seconds * (attempt + 1))
    raise last_exc
