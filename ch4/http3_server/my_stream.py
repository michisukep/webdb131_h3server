# aioquicのクラス
from aioquic.h3.events import H3Event,\
  HeadersReceived, DataReceived

# 作成したクラス
from my_application import MyApplication


# ストリームに関する機能を提供するクラス
class MyStream:

  # コンストラクタ
  def __init__(self, mycon, stream_id: int):
    self.mycon = mycon  # MyH3Connectionオブジェクト
    self.stream_id = stream_id  # ストリームID
    self.fields = {}  # フィールドの連想配列
    self.app = MyApplication(self) # アプリケーション
    self.post_data = bytes()
    self.finished = False

  # HTTP3イベントを受信したときに呼ばれる
  def h3_event_received(self, hev: H3Event):
    # イベントを出力
    print(f"     H3 Event: {hev}")

    if isinstance(hev, HeadersReceived):
      self.headers_received(hev)
    elif isinstance(hev, DataReceived):
      self.data_received(hev)

  # HeadersReceivedイベントが発生したとき呼ばれる
  def headers_received(self, hev: HeadersReceived):
    self.analyze_header(hev)
    if self.fields[":method"] == "GET":
      self.app.do_app()


  def data_received(self, hev: DataReceived):
    self.post_data = self.post_data + hev.data

    if self.fields[":method"] == "POST" and hev.stream_ended \
        and not self.finished:
      self.app.do_app()
      self.finished = True


  # イベント内のフィールドリストを連想配列に変換する
  def analyze_header(self, hev: HeadersReceived):
    for name, value in hev.headers:
      # バイト列を文字列に変換しながら登録する
      self.fields[name.decode()] = value.decode()

  # ヘッダを送信(予約)する
  def send_headers(self, status: int, fields: dict):
    # (フィールド名のバイト列,フィールド値のバイト列)というタプルの
    # 配列を作成
    headers = []
    # Statusは":status"というフィールドに格納
    headers.append((b":status", str(status).encode()))

    # 渡されたフィールドの連想配列をheaders配列に追加する
    for name, value in fields.items():
        headers.append((name.encode(), value.encode()))

    # H3Connectionオブジェクトに処理を委譲
    self.mycon.h3con.send_headers(self.stream_id, headers)

  # データを送信(予約)する
  def send_data(self, data: bytes, end_stream=True):
    # H3Connectionオブジェクトに処理を委譲
    self.mycon.h3con.send_data(
      self.stream_id, data, end_stream)


