# hameln-reading-data

## 概要
`hameln-reading-data` は、web 小説投稿サイト「ハーメルン」から読書データを取得し、作品数、話数、文字数を JSON 形式で返す FastAPI サービスです。このプロジェクトは Render でデプロイされています。

## サイト
[こちら](https://hameln-reading-data.onrender.com/docs)から実際のサイトを訪れることができます。

## 機能
- ハーメルンの読書データから作品数、話数、文字数を取得
- FastAPI を使用した迅速で軽量な API サービス
- JSON 形式でデータを提供

## インストール
このリポジトリをクローンし、必要なパッケージをインストールしてください。

```bash
git clone https://github.com/SahutoL/hameln-reading-data.git
cd hameln-reading-data
pip install -r requirements.txt
```

## 使用方法
API サーバーを起動するには以下のコマンドを実行してください。

```bash
uvicorn app.main:app --reload
```

サーバーが起動したら、ブラウザで http://127.0.0.1:8000/docs にアクセスすることで、Swagger UI で API エンドポイントを確認できます。

## 注意事項
- 当プロジェクトにおいては、そこで利用しているBasic認証には意味があまり無いと指摘できます。
- また、ハーメルンのログイン設計上、パスワードを平文で通信することになることを踏まえると、セキュリティ性が皆無であり実用性が殆ど無いことに注意してください。