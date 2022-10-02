import time

# aioquic関連のクラス
from aioquic.quic.connection import QuicConnection


# HTTP3接続に関する機能を提供するクラス
class MyConnection:
  # コンストラクタ
  def __init__(self, con: QuicConnection):
    self.qcon = con
    self.h3con = None
    self.stream_map = {}

  def udp_packet_received(self, pkt: bytes, adr: tuple):
    # パケットの解析
    self.qcon.receive_datagram(pkt, adr, time.time())
    # QUICイベントの処理
    self.handle_quic_events(self.qcon)

  # QUICイベントを処理する
  def handle_quic_events(self, con: QuicConnection):
    while True:
      # 次に処理すべきイベントを取得する
      ev = con.next_event()
      if ev is None:
        break

      # イベントを出力
      print(f"    QUIC Event: {ev}")
