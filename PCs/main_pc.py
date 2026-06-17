# main_pc.py  (Ubuntu PC)
"""
全モジュールを起動順序に従って統括する。
起動順: BT接続 → IP表示ポップアップ → 監視 → コマンド入力
"""
import bt_client, monitor, popup_manager, commander

def on_connected(rpi_ip: str):
    """PAN接続完了コールバック"""
    popup_manager.show_ip_popup(rpi_ip)      # IPポップアップ表示
    monitor.start_monitor(                   # 強度監視開始
        on_level_change=popup_manager.on_level_change
    )

if __name__ == "__main__":
    print("=== Bluetooth PAN 自動接続システム 起動 ===")
    bt_client.start_auto_connect(on_connected=on_connected)

    # 接続が確立するまでブロック（最大10秒）
    import time
    for _ in range(12):
        if bt_client._connected: break
        time.sleep(1)

    if bt_client._connected:
        commander.start_commander()   # コマンド入力ループ（ここでブロック）
    else:
        print("[MAIN] 接続失敗。終了します。")
