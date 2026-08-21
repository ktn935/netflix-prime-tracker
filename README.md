# Netflix / Prime Video 配信終了お知らせ 自動投稿Bot

Netflixの「配信終了予定」(Get Freax)、Amazon Prime Videoの「配信終了予定」(vedyro.com)を
毎日自動取得し、Xに投稿するツールです。GitHub Actionsで無料で定期実行できます。

## ⚠️ 前提として知っておいてほしいこと

- ここで使っている情報源(Get Freax / vedyro.com)は、どちらも**非公式のファンサイト**です。
  情報が100%正確とは限りません。
- サイトのデザインが変わると、スクレイピング処理が動かなくなることがあります。
  その場合は `scrape_netflix.py` / `scrape_prime.py` の正規表現部分を調整してください。
- アクセス頻度は1日1回程度に抑えています(サイトに負荷をかけすぎないため)。

## 1. ローカルでの動作確認(推奨)

Windows PCで、まず手元で正しく動くか確認します。

```bash
# 1. このフォルダに移動
cd vod_x_bot

# 2. 必要なライブラリをインストール
pip install -r requirements.txt

# 3. 投稿せず内容だけ確認(重要: 最初は必ずこちらで)
python main.py --dry-run
```

`--dry-run` を付けると実際には投稿されず、生成される文章だけが表示されます。
内容がおかしくないか確認してください。

### APIキーをローカルで設定する場合

Windowsのコマンドプロンプトなら:

```
set X_API_KEY=ここにAPIキー
set X_API_KEY_SECRET=ここにAPIキーシークレット
set X_ACCESS_TOKEN=ここにアクセストークン
set X_ACCESS_TOKEN_SECRET=ここにアクセストークンシークレット
```

を実行してから `python main.py --dry-run` を実行してください。
(このコマンドプロンプトを閉じると設定は消えます。毎回設定し直すか、
 後述のGitHub Actions運用に切り替えるのがおすすめです)

## 2. GitHub Actionsでの自動実行セットアップ

### 2-1. GitHubリポジトリを作成

1. https://github.com で新規リポジトリを作成(Private推奨)
2. このフォルダの中身(README.mdやmain.pyなど全部)をアップロード
   - GitHub Desktop を使うと簡単です: https://desktop.github.com/

### 2-2. APIキーをGitHub Secretsに登録

**これが最重要ステップです。** APIキーをコードに直接書かず、GitHubの「Secrets」という
安全な場所に保存します。

1. リポジトリのページで `Settings` タブを開く
2. 左メニューの `Secrets and variables` → `Actions` を選択
3. `New repository secret` ボタンを押し、以下の4つを1つずつ登録:

| Name(名前) | Value(値) |
|---|---|
| `X_API_KEY` | 取得したAPI Key |
| `X_API_KEY_SECRET` | 取得したAPI Key Secret |
| `X_ACCESS_TOKEN` | 取得したAccess Token |
| `X_ACCESS_TOKEN_SECRET` | 取得したAccess Token Secret |

### 2-3. 動作確認

1. リポジトリの `Actions` タブを開く
2. `Daily VOD Post` ワークフローを選択
3. `Run workflow` ボタンで手動実行してみる
4. 緑のチェックマークが付けば成功。ログで投稿内容を確認できます

### 2-4. 自動実行のタイミングを変える場合

`.github/workflows/daily_post.yml` の中の

```yaml
- cron: "0 21 * * *"
```

を編集します。この時刻は **UTC(協定世界時)** なので、日本時間から9時間引いた値を書きます。
(例: 日本時間の朝8時に投稿したい → UTC 23時 → `"0 23 * * *"`)

## 3. ファイル構成

```
vod_x_bot/
├── main.py              # 実行の起点
├── scrape_netflix.py     # Netflixの配信終了情報を取得
├── scrape_prime.py       # Prime Videoの配信終了情報を取得
├── compose.py            # 投稿文を組み立てる
├── post_x.py              # Xへの投稿処理
├── requirements.txt
└── .github/workflows/daily_post.yml   # 自動実行の設定
```

## 4. うまく動かないときは

- `python main.py --dry-run` を実行してエラーメッセージを確認してください
- 「Netflix情報の取得に失敗しました」等のエラーが出る場合、サイト構造が
  変わった可能性があります。ブラウザで実際のページを開いて構造を見比べてください
- X APIの認証エラーが出る場合は、GitHub SecretsのAPIキーが正しいか、
  X Developer PortalでApp権限が「Read and write」になっているか確認してください
