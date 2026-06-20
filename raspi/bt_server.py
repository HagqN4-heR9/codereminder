# bt_server.py  (Raspberry Pi)
"""
起動時にBluetoothをdiscoverable状態にし、
PANのNAPロールとしてbt-panを自動起動する。
"""
import subprocess, time, sys

RPI_BT_IFACE = "hci0"
RPI_PAN_IP   = "192.168.44.2"
PAN_NETMASK  = "24"

def setup_bluetooth():
    """BTアダプターを起動・discoverable設定"""
    cmds = [
        ["bluetoothctl", "power",        "on"],
        ["bluetoothctl", "discoverable", "on"],
        ["bluetoothctl", "pairable",     "on"],
    ]
    for cmd in cmds:
        subprocess.run(cmd, check=True)
        time.sleep(0.3)
    print("[BT] discoverable ON")

def start_pan_nap():
    """NAPロールでbt-panを起動しIPを付与"""
    subprocess.Popen(["sudo", "bt-pan", "nap", RPI_BT_IFACE])
    time.sleep(2)   # インターフェース生成を待つ
    subprocess.run([
        "sudo", "ip", "addr", "add",
        f"{RPI_PAN_IP}/{PAN_NETMASK}", "dev", "bnep0"
    ])
    subprocess.run(["sudo", "ip", "link", "set", "bnep0", "up"])
    print(f"[PAN] NAPモード起動 IP={RPI_PAN_IP}")

if __name__ == "__main__":
    setup_bluetooth()
    start_pan_nap()
    print("[BT_SERVER] 接続待機中...")
    # このプロセスはbt-panの親として常駐
    try:
        while True: time.sleep(60)
    except KeyboardInterrupt:
        print("[BT_SERVER] 終了")
