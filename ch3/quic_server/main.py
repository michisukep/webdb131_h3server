from argparse import ArgumentParser

from my_server import MyServer

if __name__ == '__main__':
  # コマンドラインを解析する
  parser = ArgumentParser()
  parser.add_argument("--host", type=str, default="0.0.0.0")
  parser.add_argument("--port", type=int, default=8443)
  parser.add_argument("--cert", type=str)
  parser.add_argument("--key", type=str)
  options = parser.parse_args()

  # QUICサーバーを作成
  serv = MyServer(options.host, options.port,
                  options.cert, options.key)
  # QUICサーバーを開始
  serv.start()
