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
        res = subprocess.run(
            ["ping", "-c", "1", "-W", "1", host],
            capture_output=True, text=True, timeout=2
        )
        m = re.search(r"time=([d.]+)", res.stdout)
        return float(m.group(1)) if m else -1.0
    except Exception:
        return -1.0

def start_monitor(on_level_change=None):
    """
    バックグラウンドで監視ループを起動。
    レベルが変化したとき on_level_change(level, rtt_ms) を呼ぶ。
    """
    def _loop():
        prev_level = 4
        while True:
            rtt   = _ping_once(RPI_IP)
            level = rtt_to_level(rtt)
            if level != prev_level:
                prev_level = level
                print(f"[MON] 強度レベル変化: {level}  RTT={rtt:.1f}ms")
                if on_level_change:
                    on_level_change(level, rtt)
            time.sleep(1)
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
