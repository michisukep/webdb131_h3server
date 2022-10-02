import time

# aioquic関連のクラス
from aioquic.quic.connection import QuicConnection
from aioquic.quic.events import \
  HandshakeCompleted, StreamDataReceived
from aioquic.h3.connection import H3Connection

# 作成したクラス
from my_stream import MyStream



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

      # StreamDataReceivedイベントの処理
      if isinstance(ev, HandshakeCompleted):
        self.h3con = H3Connection(con)
      elif isinstance(ev, StreamDataReceived):
        self.stream_data_received(ev)


  # QUICイベントを処理する
  def stream_data_received(self, ev: StreamDataReceived):

    # ストリームデータが到着したらMyStreamオブジェクトを取得
    stream = self.stream_map.get(ev.stream_id)
    if stream is None:
      # MyStreamオブジェクトがなければ新規作成
      stream = MyStream(self, ev.stream_id)
      self.stream_map[ev.stream_id] = stream

    # 処理すべきHTTP3のイベントを取り出す
    for hev in self.h3con.handle_event(ev):
      stream.h3_event_received(hev)

