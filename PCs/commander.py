# commander.py  (Ubuntu PC)
"""
ターミナルからコマンドを入力し、
UTF-8文字列 + 4バイトbig-endianサイズヘッダに変換してラズパイへ送信。
C++側は ntohl() でサイズを読み出し std::string にパースする。
"""
import socket, struct

RPI_IP   = "192.168.44.2"
CMD_PORT = 9997

def send_command(sock: socket.socket, command: str):
    """コマンド文字列を [4バイトサイズ]+[UTF-8文字列] に変換して送信"""
    payload = command.encode("utf-8")
    header  = struct.pack(">I", len(payload))  # big-endian 4バイト
    sock.sendall(header + payload)
    print(f"[CMD] 送信: {command}  ({len(payload)} bytes)")

def start_commander():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((RPI_IP, CMD_PORT))
        print(f"[CMD] ラズパイに接続: {RPI_IP}:{CMD_PORT}")
        print("コマンド例: LED_ON / LED_OFF / MSG:テキスト / exit")
        while True:
            cmd = input(">>> ").strip()
            if not cmd: continue
            if cmd.lower() == "exit": break
            send_command(s, cmd)
