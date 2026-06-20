# popup_manager.py  (Ubuntu PC)
"""
【IP通知ポップアップ】
  ・接続完了時にラズパイIPを表示
  ・ユーザーが手動で閉じるまで消えない

【警告ポップアップ】
  ・強度レベル2以下で画面右端に出現
  ・レベル3以上に回復したら自動消去
"""
import tkinter as tk
import threading

_warn_window = None   # 警告ウィンドウの参照（None=非表示）
_tk_lock = threading.Lock()

# ── IP通知ポップアップ ──────────────────────────────────
def show_ip_popup(ip: str):
    """接続完了時に呼ぶ。ユーザーが閉じるまで表示し続ける"""
    def _build():
        win = tk.Tk()
        win.title("Bluetooth PAN 接続完了")
        win.geometry("340x160+600+300")
        win.resizable(False, False)
        win.configure(bg="#EBF5FB")

        tk.Label(win, text="接続しました", font=("Arial",14,"bold"),
                 bg="#EBF5FB", fg="#1E3A5F").pack(pady=(20,4))
        tk.Label(win, text=f"Raspberry Pi IP", font=("Arial",10),
                 bg="#EBF5FB", fg="#555").pack()
        tk.Label(win, text=ip, font=("Courier New",18,"bold"),
                 bg="#EBF5FB", fg="#2E75B6").pack(pady=4)
        tk.Button(win, text="  閉じる  ", command=win.destroy,
                  bg="#2E75B6", fg="white", font=("Arial",11)).pack(pady=10)
        win.mainloop()
    threading.Thread(target=_build, daemon=True).start()

# ── 警告ポップアップ ────────────────────────────────────
LEVEL_CONFIG = {
    2: {"bg":"#FFF3CD","fg":"#856404","title":"接続不安定","msg":"接続が不安定です\n(レベル2)"},
    1: {"bg":"#F8D7DA","fg":"#721C24","title":"接続危険" ,"msg":"接続が非常に不安定です\n(レベル1)"},
    0: {"bg":"#D32F2F","fg":"#FFFFFF","title":"圏外"     ,"msg":"接続が切断されました\n(圏外)"},
}

def _get_screen_right(win, width=260, height=120):
    """画面右端の座標を計算する"""
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x  = sw - width - 20
    y  = sh - height - 60
    return f"{width}x{height}+{x}+{y}"

def show_warning(level: int):
    """強度レベル2以下で警告ウィンドウを画面右に表示（既存は更新）"""
    global _warn_window
    cfg = LEVEL_CONFIG.get(level)
    if cfg is None: return

    def _build():
        global _warn_window
        with _tk_lock:
            if _warn_window and _warn_window.winfo_exists():
                _warn_window.destroy()
            win = tk.Toplevel() if False else tk.Tk()
            win.title(cfg["title"])
            win.configure(bg=cfg["bg"])
            win.attributes("-topmost", True)  # 常に最前面
            win.overrideredirect(True)         # タイトルバー非表示
            win.geometry(_get_screen_right(win))
            tk.Label(win, text=f"⚠ {cfg["title"]}",
                     font=("Arial",12,"bold"),
                     bg=cfg["bg"], fg=cfg["fg"]).pack(pady=(12,4), padx=16)
            tk.Label(win, text=cfg["msg"],
                     font=("Arial",10),
                     bg=cfg["bg"], fg=cfg["fg"]).pack(padx=16)
            _warn_window = win
            win.mainloop()
    threading.Thread(target=_build, daemon=True).start()

def hide_warning():
    """強度が回復したとき（レベル3以上）に警告を自動削除"""
    global _warn_window
    with _tk_lock:
        if _warn_window:
            try:
                _warn_window.destroy()
            except Exception:
                pass
            _warn_window = None
    print("[POPUP] 警告を削除")

def on_level_change(level: int, rtt: float):
    """monitor.pyから呼ばれるコールバック"""
    if level <= 2:
        show_warning(level)
    else:
        hide_warning()
