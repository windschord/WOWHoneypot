# WOWHoneypot2:

This is project still workin on.

[WOWHoneypot](https://github.com/morihisa/WOWHoneypot) に以下の機能を付加・変更したHoneypotです。

- Pythonロギングによりログのカスタマイズが可能
- ElasticsearchにアクセスログとHuntingログの送信が可能
- 設定ファイルをPython形式に変更

## 特徴
- 構築が簡単
- HTTP リクエストをまるっと保存
- デフォルト200 OK
- マッチ&レスポンス

## 必要なもの
- Python3

## 構築方法1 (Docker)
```
$ sudo ufw default DENY
$ sudo ufw allow 80/tcp
$ sudo ufw allow 8080/tcp
※ SSH のアクセスポートも環境に合わせて追加してください。
$ sudo ufw enable
$ sudo vi /etc/ufw/before.rules
※ 「*filter」より前に下記の4行を追記する。
———————————————————————————
*nat
:PREROUTING ACCEPT [0:0]
-A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
COMMIT
———————————————————————————
$ sudo ufw reload

$ docker run -p 8080:8080 windschord/wowhoneypot wowhoneypot.py
```

## 構築方法2 (Ubuntu 18.04.4 LTS)
```
$ sudo ufw default DENY
$ sudo ufw allow 80/tcp
$ sudo ufw allow 8080/tcp
※ SSH のアクセスポートも環境に合わせて追加してください。
$ sudo ufw enable
$ sudo vi /etc/ufw/before.rules
※ 「*filter」より前に下記の4行を追記する。
———————————————————————————
*nat
:PREROUTING ACCEPT [0:0]
-A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
COMMIT
———————————————————————————
$ sudo ufw reload
$ cd ~/
$ git clone https://github.com/morihisa/WOWHoneypot.git wowhoneypot
$ cd wowhoneypot
$ python3 ./wowhoneypot.py
```
### Systemd
```
sudo cp WOWHoneypot.service /etc/systemd/system/
sudo cp WOWHoneypotTcpLog.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl start WOWHoneypot
sudo systemctl start WOWHoneypotTcpLog

sudo systemctl status WOWHoneypot
sudo systemctl status WOWHoneypotTcpLog

sudo systemctl enable WOWHoneypot
sudo systemctl enable WOWHoneypotTcpLog
```

## 動作確認
- ブラウザでハニーポットの IP アドレスにアクセスして、何かしらの HTML ファイルが返ってきたら OK です。

## ログファイル
- log/wowhoneypot.log
- WOWHoneypot の動作ログが記録されます。
- log/access_log
- アクセスログが記録されます。

## elastic search
```bash
curl -XPUT 'localhost:9200/wowhoneypot'
```

## GeoIPの使用
下記のURLからデータベースファイル（GeoLite2-City.mmdb）をダウンロードする。

https://dev.maxmind.com/geoip/geoip2/geolite2/

config.txtの`geoipdbpath`に`GeoLite2-City.mmdb`のパスを設定する。

pip3 install geoip2

## ハンティング機能(WOWHoneypot 1.1 で追加)
- ハンティング機能は、あらかじめ指定しておいた文字列が、要求内容に含まれていた場合に、その文字列をログとして保存します。
- 使い方の例として、wget のようなファイルをダウンロードするコマンドに続いて URL が指定されている文字列を抽出することができます。
- デフォルト設定では無効化されています。利用する場合は、config.txt の「hunt_enable」をTrueに変更してください。
- 抽出する文字列は、art ディレクトリの huntrules.txt ファイルに1行につき1つ指定してください(正規表現で指定可能)。
- 抽出したログは、log ディレクトリの hunting.log に保存されます(\[日時\] 送信元IP 一致した文字列)。
---
- hunting.log ファイルから、URL を抽出して VirusTotal へサブミットするサンプルスクリプト(chase-url.py)を公開しました。
- chase-url.py を利用する場合、requests ライブラリが必要です($ pip3 install requests)。
- 実行前に、VirusTotal API Key を取得して、chase-url.py に記載してください。
- 1日や1時間に1回程度実行するといいと思います。ただし VirusTotal API の上限に引っかからないように注意してください。
- サブミットするファイルは、**メモリへキャッシュとして保存しますが、ディスクには保存しません。**

## Licence

[BSD License](https://github.com/morihisa/WOWHoneypot/blob/master/LICENSE)
