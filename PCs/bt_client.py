# bt_client.py  (Ubuntu PC)
"""
・ラズパイのBTアドレスを検出してPANUロールで接続
・未接続時は1秒ごとにリトライ、10回失敗でBTスリープ
・接続成功時に on_connected(ip) コールバックを呼ぶ
"""
import subprocess, time, threading

RPI_BT_MAC  = "XX:XX:XX:XX:XX:XX"  # ラズパイのMACアドレスに変更
PC_PAN_IP   = "192.168.44.1"
RPI_PAN_IP  = "192.168.44.2"
PAN_NETMASK = "24"
RETRY_MAX   = 10   # 10秒でスリープ

_connected   = False
_retry_count = 0

def _run(cmd: list) -> bool:
    """コマンドを実行し成功/失敗をboolで返す"""
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def _bt_sleep():
    """Bluetoothアダプターをスリープ（power off）"""
    subprocess.run(["bluetoothctl", "power", "off"])
    print("[BT] 10秒間接続できなかったためBTスリープ")

def _setup_pan_ip():
    """bnep0にIPを付与"""
    subprocess.run(["sudo","ip","addr","add",
                    f"{PC_PAN_IP}/{PAN_NETMASK}","dev","bnep0"])
    subprocess.run(["sudo","ip","link","set","bnep0","up"])

def connect_pan(on_connected=None):
    """
    PANUロールでラズパイに接続を試みる。
    成功: on_connected(rpi_ip) を呼び True を返す
    失敗: False を返す
    """
    global _connected
    ok = _run(["sudo","bt-pan","client", RPI_BT_MAC])
    if not ok:
        return False
    time.sleep(2)
    _setup_pan_ip()
    _connected = True
    print(f"[PAN] 接続完了 ラズパイIP={RPI_PAN_IP}")
    if on_connected:
        on_connected(RPI_PAN_IP)
    return True

def start_auto_connect(on_connected=None):
    """
    バックグラウンドで接続監視ループを起動。
    1秒ごとにリトライし10回でBTスリープ。
    """
    def _loop():
        global _retry_count, _connected
        while not _connected:
            print(f"[BT] 接続試行 {_retry_count+1}/{RETRY_MAX}")
            if connect_pan(on_connected):
                return
            _retry_count += 1
            if _retry_count >= RETRY_MAX:
                _bt_sleep()
                return
            time.sleep(1)
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
