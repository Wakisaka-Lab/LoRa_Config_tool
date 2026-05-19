import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import sys
import os

def resource_path(relative_path):
    """PyInstallerで実行された場合と、通常スクリプトとして実行された場合の両方でファイルのパスを解決する"""
    try:
        # PyInstaller実行時は _MEIPASS に一時解凍フォルダのパスが入る
        base_path = sys._MEIPASS
    except Exception:
        # 通常のPythonスクリプトとして実行している場合はカレントディレクトリ
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ToolTip:
    """ウィジェットにマウスホバーで表示されるツールチップを作成するクラス"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) # ウィンドウの枠を消す
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("sans-serif", "9", "normal"))
        label.pack(ipadx=4, ipady=2)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class LoRaConfigTool:
    def __init__(self, root):
        self.root = root
        self.root.title("LoRa P2P 設定ツール")
        self.root.geometry("500x480")

        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except Exception as e:
            print(f"アイコンの読み込みをスキップしました: {e}")

        # --- シリアルポート設定UI ---
        frame_port = ttk.LabelFrame(root, text="シリアルポート設定")
        frame_port.pack(padx=10, pady=5, fill="x")
        
        # ポート選択
        self.port_combo = ttk.Combobox(frame_port, state="readonly", width=15)
        self.port_combo.pack(side="left", padx=5, pady=5)
        self.update_ports()
        
        btn_refresh = ttk.Button(frame_port, text="更新", command=self.update_ports, width=5)
        btn_refresh.pack(side="left", padx=5, pady=5)

        # ボーレート選択
        ttk.Label(frame_port, text="ボーレート:").pack(side="left", padx=(10, 0))
        self.baud_combo = ttk.Combobox(frame_port, values=["9600", "19200", "57600", "115200"], state="readonly", width=8)
        self.baud_combo.set("9600") # デフォルトを9600に設定
        self.baud_combo.pack(side="left", padx=5, pady=5)


        # --- パラメータ設定UI ---
        frame_param = ttk.LabelFrame(root, text="P2Pパラメータ設定")
        frame_param.pack(padx=10, pady=5, fill="both", expand=True)

        # 周波数
        lbl_freq = ttk.Label(frame_param, text="周波数:")
        lbl_freq.grid(row=0, column=0, sticky="e", padx=5, pady=10)
        ToolTip(lbl_freq, "値の範囲 (日本国内): 920500000 ～ 928100000")
        
        self.var_freq = tk.StringVar(value="922500000")
        ttk.Entry(frame_param, textvariable=self.var_freq).grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        # 出力
        lbl_pwr = ttk.Label(frame_param, text="出力:")
        lbl_pwr.grid(row=1, column=0, sticky="e", padx=5, pady=10)
        ToolTip(lbl_pwr, "値の範囲: 2 ～ 20\nおすすめ(迷ったらこれ): 13\n※14以上は電波法アウト")
        
        self.var_pwr = tk.StringVar(value="13")
        ttk.Spinbox(frame_param, from_=2, to=20, textvariable=self.var_pwr).grid(row=1, column=1, sticky="ew", padx=5, pady=10)

        # 拡散係数
        lbl_sf = ttk.Label(frame_param, text="拡散係数:")
        lbl_sf.grid(row=2, column=0, sticky="e", padx=5, pady=10)
        ToolTip(lbl_sf, "値の範囲: 7, 8, 9, 10, 11, 12\nおすすめ: 遠くまで飛ばしたい時は 12")
        
        self.var_sf = tk.StringVar(value="12")
        ttk.Combobox(frame_param, values=["7", "8", "9", "10", "11", "12"], textvariable=self.var_sf, state="readonly").grid(row=2, column=1, sticky="ew", padx=5, pady=10)

        # 帯域幅
        lbl_bw = ttk.Label(frame_param, text="帯域幅:")
        lbl_bw.grid(row=3, column=0, sticky="e", padx=5, pady=10)
        ToolTip(lbl_bw, "値の範囲: 125, 250, 500\nおすすめ: 125")
        
        self.var_bw = tk.StringVar(value="125")
        ttk.Combobox(frame_param, values=["125", "250", "500"], textvariable=self.var_bw, state="readonly").grid(row=3, column=1, sticky="ew", padx=5, pady=10)

        # SyncWord
        lbl_sync = ttk.Label(frame_param, text="SyncWord:")
        lbl_sync.grid(row=4, column=0, sticky="e", padx=5, pady=10)
        ToolTip(lbl_sync, "値の範囲: 0 ～ FF\n※適当な16進数で良いが、0だと通信できないことがある")
        
        self.var_sync = tk.StringVar(value="12")
        ttk.Entry(frame_param, textvariable=self.var_sync).grid(row=4, column=1, sticky="ew", padx=5, pady=10)

        frame_param.columnconfigure(1, weight=1)

        # --- 実行ボタン ---
        self.btn_send = ttk.Button(root, text="モジュールに一括設定を書き込む", command=self.write_config)
        self.btn_send.pack(padx=10, pady=10, fill="x", ipadx=10, ipady=10)

        # --- ログ表示UI ---
        self.txt_log = tk.Text(root, height=8, state="disabled", bg="#f0f0f0")
        self.txt_log.pack(padx=10, pady=5, fill="both", expand=True)

    def update_ports(self):
        """PCに接続されているCOMポートを取得し、コンボボックスを更新します。"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
        else:
            self.port_combo.set("ポートなし")

    def log(self, msg):
        """処理状況や通信内容をテキストボックスに出力します。"""
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    def write_config(self):
        """UIの入力値からコマンドリストを生成し、別スレッドで送信処理を開始します。"""
        port = self.port_combo.get()
        if not port or port == "ポートなし":
            messagebox.showerror("エラー", "シリアルポートを選択してください。")
            return
            
        baudrate = int(self.baud_combo.get())

        # --- 周波数のバリデーション (日本国内の規定範囲) ---
        try:
            freq_val = int(self.var_freq.get())
            if not (920500000 <= freq_val <= 928100000):
                messagebox.showerror("入力エラー", "日本の電波法（特定小電力無線局）で許可されている周波数は\n920.5 MHz ～ 928.1 MHz です。\n\n920500000 ～ 928100000 の範囲で入力してください。")
                return
        except ValueError:
            messagebox.showerror("入力エラー", "周波数は半角数字で入力してください。")
            return

        commands = [
            f"p2p set_freq {self.var_freq.get()}",
            f"p2p set_pwr {self.var_pwr.get()}",
            f"p2p set_sf {self.var_sf.get()}",
            f"p2p set_bw {self.var_bw.get()}",
            f"p2p set_sync {self.var_sync.get()}",
            "p2p save"
        ]

        threading.Thread(target=self._send_commands, args=(port, baudrate, commands), daemon=True).start()

    def _send_commands(self, port, baudrate, commands):
        """シリアルポートを開き、生成したコマンドを順番にモジュールへ送信します。"""
        self.btn_send.config(state="disabled")
        self.log(f"--- {port} ({baudrate}bps) に接続中 ---")
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                for cmd in commands:
                    self.log(f"送信: {cmd}")
                    ser.write((cmd + "\r").encode('ascii')) 
                    time.sleep(0.2) 
                    
                    res = ser.read_all().decode('ascii', errors='replace').strip()
                    if res:
                        self.log(f"受信: {res}")
                
                self.log("--- 設定完了 ---")
                messagebox.showinfo("成功", "設定の書き込みが完了しました。")
        except Exception as e:
            self.log(f"エラー: {e}")
            messagebox.showerror("通信エラー", str(e))
        finally:
            self.btn_send.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoRaConfigTool(root)
    root.mainloop()