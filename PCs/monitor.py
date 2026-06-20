# monitor.py  (Ubuntu PC)
"""
1秒ごとにラズパイへpingを送りRTTを計測。
4段階レベルに変換し、変化時にコールバックを通知する。
"""
import subprocess, threading, time, re

RPI_IP = "192.168.44.2"

# RTT → レベル変換テーブル
def rtt_to_level(rtt_ms: float) -> int:
    if rtt_ms <   0:  return 0  # タイムアウト
    if rtt_ms <=  50: return 4  # 良好
    if rtt_ms <= 150: return 3  # 普通
    if rtt_ms <= 300: return 2  # 不安定（警告閾値）
    if rtt_ms <= 500: return 1  # 危険
    return 0                    # 圏外

def _ping_once(host: str) -> float:
    """pingを1回実行しRTT(ms)を返す。失敗時は-1.0"""
    try:
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
