import socket, time

# aioquic関連のクラス
from aioquic.buffer import Buffer
from aioquic.quic import packet
from aioquic.quic.configuration \
  import QuicConfiguration
from aioquic.quic.packet import QuicHeader
from aioquic.quic.connection import QuicConnection

# 作成したクラス
from my_connection import MyConnection


# QUIC Serverを実現するクラス
class MyServer:
  PACKET_SIZE = 65536

  # コンストラクタ
  #  ip: 待ち受けるIPアドレス
  #  port: 待ち受けるポート
  #  cert: サーバー証明書ファイルのパス
  #  key: 鍵ファイルのパス
  def __init__\
    (self, ip: str, port: int, cert: str, key: str):
    self.ip = ip
    self.port = port
    # aioquicの構成オブジェクトを作成
    self.cfg = QuicConfiguration(
      alpn_protocols=["h3"],
      is_client=False,
      max_datagram_frame_size=self.PACKET_SIZE
    )
    # サーバー証明書を読み込む
    self.cfg.load_cert_chain(cert, key)
    # サーバーソケットを作成する
    self.server_socket = \
      socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 接続を管理する連想配列
    self.con_map = {}

  # サーバーを開始する
  def start(self):
    # サーバーソケットの待ち受けを開始する
    server_addr = (self.ip, self.port)
    print(f"Opening port: {server_addr}")
    self.server_socket.bind(server_addr)

    while True:
      # パケットの到着を待つ
      data, client_adr = \
        self.server_socket.recvfrom(self.PACKET_SIZE)
      # パケットが到着したらイベントハンドラを呼び出す
      self.udp_packet_received(data, client_adr)

  # パケットが到着した時に呼ばれる
  def udp_packet_received(self, pkt: bytes, adr: tuple):
    # パケットヘッダの解析
    hdr = packet.pull_quic_header(
      Buffer(data=pkt), self.cfg.connection_id_length)
    # パケットヘッダ詳細の出力
    self.print_packet_header(pkt, hdr, '->')

    # 保管された接続オブジェクトを取得
    mycon = self.con_map.get(hdr.destination_cid)
    # Initialパケットだったらハンドシェイクを開始する
    if mycon is None \
      and hdr.packet_type == packet.PACKET_TYPE_INITIAL:
      # aioquicの接続オブジェクトを作成
      con = QuicConnection(
        configuration=self.cfg,
        original_destination_connection_id=hdr.destination_cid
      )
      # MyConnectionオブジェクトを作成
      mycon = MyConnection(con)
      # MyCOnnectionブジェクトを保管
      self.con_map[con.host_cid] = mycon

    if mycon is not None:
      mycon.udp_packet_received(pkt, adr)

      # クライアントにパケットを送信
      self.send_packets(mycon.qcon)


  # パケットヘッダの詳細を出力
  def print_packet_header\
     (self, pkt: bytes, hdr: QuicHeader, prefix: str):
    print(f"{prefix} version={hdr.version}"
      + f" type={self.packet_type_name(hdr.packet_type)}"
      + f" scid={hdr.source_cid.hex()}"
      + f" dcid={hdr.destination_cid.hex()}"
      + f" token={hdr.token.hex()} len={len(pkt)}")

  # パケットタイプを文字列で取得する
  def packet_type_name(self, typ: int):
    if typ & packet.PACKET_LONG_HEADER == 0:
      return "Short"
    elif typ == packet.PACKET_TYPE_INITIAL:
      return "Initial"
    elif typ == packet.PACKET_TYPE_ZERO_RTT:
      return "0-RTT"
    elif typ == packet.PACKET_TYPE_HANDSHAKE:
      return "Handshake"
    elif typ == packet.PACKET_TYPE_RETRY:
      return "Retry"
    else:
      return "Unkonwn"


  # 送るべきパケットをクライアントに送信する
  def send_packets(self, con: QuicConnection):
    # 送るべきパケットを１つずつ取り出し、UDPパケットとしてクライアントに送信する
    for pkt, adr in \
        con.datagrams_to_send(now=time.time()):
      self.server_socket.sendto(pkt, adr)
      # 送信したパケットヘッダ詳細の出力
      hdr = packet.pull_quic_header(
        Buffer(data=pkt),
        self.cfg.connection_id_length)
      self.print_packet_header(pkt, hdr, '<-')
