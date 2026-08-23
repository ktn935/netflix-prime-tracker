# -*- coding: utf-8 -*-
"""
Xへの投稿処理。
APIキー類は環境変数から読み込む(コードに直接書かない)。

必要な環境変数:
  X_API_KEY
  X_API_KEY_SECRET
  X_ACCESS_TOKEN
  X_ACCESS_TOKEN_SECRET
"""
import io
import os

import tweepy


def _credentials():
    return (
        os.environ["X_API_KEY"].strip(),
        os.environ["X_API_KEY_SECRET"].strip(),
        os.environ["X_ACCESS_TOKEN"].strip(),
        os.environ["X_ACCESS_TOKEN_SECRET"].strip(),
    )


def get_client():
    api_key, api_secret, access_token, access_secret = _credentials()
    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )


def get_api_v1():
    """画像アップロードにはv1.1 APIが必要"""
    api_key, api_secret, access_token, access_secret = _credentials()
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    return tweepy.API(auth)


def _upload_image_bytes(image_bytes):
    api = get_api_v1()
    media = api.media_upload(filename="collage.png", file=io.BytesIO(image_bytes))
    return media.media_id


def post_tweet(text: str, images=None):
    client = get_client()
    media_ids = [_upload_image_bytes(img) for img in images] if images else None
    if media_ids:
        response = client.create_tweet(text=text, media_ids=media_ids)
    else:
        response = client.create_tweet(text=text)
    return response
