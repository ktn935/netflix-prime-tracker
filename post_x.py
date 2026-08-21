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
import os
import tweepy


def get_client():
    api_key = os.environ["X_API_KEY"].strip()
    api_secret = os.environ["X_API_KEY_SECRET"].strip()
    access_token = os.environ["X_ACCESS_TOKEN"].strip()
    access_secret = os.environ["X_ACCESS_TOKEN_SECRET"].strip()

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )
    return client


def post_tweet(text: str):
    client = get_client()
    response = client.create_tweet(text=text)
    return response
