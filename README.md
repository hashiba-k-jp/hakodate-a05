# hakodate-a05
Hack U KOSEN 2021 team: hakodate-a05

# 使用時の注意
環境変数に以下のものを追加すること
- ACCESS_TOKEN (LINE APIのアクセストークン)
- CEHNEL_SECRET (LINE APIのアクセスシークレット)
- ROOT_URL (サービスのルートURL)
- IS_DEBUG (デバッグ用のフラグ。文字列Trueでデバッグモードを有効化。それ以外では無効)
- DATABASE_URL (データベースの接続先エンドポイント。構成は下記の通り)

# DATABASE_URLの仕様
```bash
postgres://{USER_NAME}:{USER_PASSWORD}@{HOST_URL}:{HOST_PORT}/{DATABASE_NAME}
```

# 実行環境
## 下記のものをインストールすること
- PostgreSQL (version 13.5)
- Python3 (requirements.txtに記載のライブラリがすべて実行できるバージョン)

## 下記のものを用意すること
- ドメイン(サブドメインでも可)
- ドメインに対して発行されたSSL証明書