# WOWHoneypot2:

This is project still working on.

[WOWHoneypot](https://github.com/morihisa/WOWHoneypot) に以下の機能を付加・変更したHoneypotです。

- Pythonロギングによりログのカスタマイズが可能
- ElasticsearchにアクセスログとHuntingログの送信が可能 (転送失敗時のリトライ機能)
- 設定ファイルをPython形式に変更
- Dockerコンテナ対応

[![dockeri.co](https://dockeri.co/image/windschord/wowhoneypot2)](https://hub.docker.com/r/windschord/wowhoneypot2)

## 特徴
- 構築が簡単
- HTTP リクエストをまるっと保存
- デフォルト200 OK
- マッチ&レスポンス

## 必要なもの
- docker or Python3.8

## 構築方法1 (Docker)
``` shell script
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

$ docker run -it -p 8080:8080 windschord/wowhoneypot wowhoneypot.py
```

**Dockerの場合は実行時のh環境変数を指定することで設定が可能です。指定可能な値の詳細は[config_docker.py](https://github.com/windschord/WOWHoneypot2/blob/master/config_docker.py)を参照してください。**

### 実行例
* ハンティング機能を有効にするには環境変数にしてください。

    ```shell script
    docker run -it -e WOWHONEYPOT_HUNT_ENABLE=True \
                   -p 8080:8080 \
                   windschord/wowhoneypot2
    ```

* Elasticserchのホストを指定したい場合などは環境変数に指定してください。
    
    ```shell script
    docker run -it -e ES_SERVER_HOSTS=192.168.1.123,192.168.1.234 \
                   -p 8080:8080 \
                   windschord/wowhoneypot2
    ```

* GEOIPを有効にしたい場合は、[maxmindからデータベースファイル（GeoLite2-City.mmdb）](https://dev.maxmind.com/geoip/geoip2/geolite2/)をダウンロードし、環境変数でGEOIPのDBファイルのパス、そのファイルをマウントしてください。
    
    ```shell script
    docker run -it -e ES_SERVER_HOSTS=192.168.11.48 \
                   -e GEOIP_PATH=/GeoLite2-City.mmdb \
                   -v `pwd`/GeoLite2-City.mmdb:/GeoLite2-City.mmdb \
                   -p 8080:8080 \
                   windschord/wowhoneypot2
    ```

* ログファイルやElasticserchへ再転送データなどを永続化したい場合はボリュームをマウントしてください。

    ```shell script
    docker run -it -v `pwd`/log:/usr/src/WOWHoneypot/log \
                   -v `pwd`/es_failed:/usr/src/WOWHoneypot/es_failed \
                   -v `pwd`/hunting_queue.db:/usr/src/WOWHoneypot/hunting_queue.db \
                   -p 8080:8080 \
                   windschord/wowhoneypot2
    ```


## [非推奨] 構築方法2 (Ubuntu 18.04.4 LTS)
``` shell script
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
sudo systemctl daemon-reload
sudo systemctl start WOWHoneypot
sudo systemctl enable WOWHoneypot
```

## 動作確認
- ブラウザでハニーポットの IP アドレスにアクセスして、何かしらの HTML ファイルが返ってきたら OK です。

## ログファイル
- log/wowhoneypot.log
- WOWHoneypot の動作ログが記録されます。
- log/access_log
- アクセスログが記録されます。

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
