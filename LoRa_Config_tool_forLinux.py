import serial
import serial.tools.list_ports
import time
import sys

def select_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("エラー: シリアルポートが見つかりません。（USBが認識されているか確認してください）")
        sys.exit(1)
    
    print("\n--- 接続可能なポート ---")
    for i, port in enumerate(ports):
        print(f"[{i}] {port.device} - {port.description}")
    
    while True:
        try:
            idx = input(f"\n使用するポートの番号を選択してください (0-{len(ports)-1}): ")
            if idx.strip() == "":
                continue
            idx = int(idx)
            if 0 <= idx < len(ports):
                return ports[idx].device
            else:
                print("範囲外の番号です。")
        except ValueError:
            print("数字を入力してください。")

def get_input(prompt, default, val_type=int):
    while True:
        val = input(f"{prompt} [デフォルト: {default}]: ").strip()
        if not val:
            return default
        try:
            if val_type == int:
                return int(val)
            return val
        except ValueError:
            print("無効な入力フォーマットです。")

def send_commands(port, baudrate, commands):
    print(f"\n=== {port} ({baudrate}bps) に接続して書き込みを開始します ===")
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            for cmd in commands:
                print(f"送信: {cmd}")
                ser.write((cmd + "\r").encode('ascii'))
                time.sleep(0.2)
                
                res = ser.read_all().decode('ascii', errors='replace').strip()
                if res:
                    print(f"受信: {res}")
            print("\n--- 設定完了 ---")
    except serial.SerialException as e:
        print(f"\n通信エラー: {e}")
        print("※ Linuxの場合、シリアルポートへのアクセス権限がない可能性があります。")
        print("  'sudo usermod -aG dialout $USER' を実行し、再起動を試してください。")

def main():
    print("=== LoRa P2P 設定ツール (Linux CLI版) ===")
    
    port = select_port()
    baudrate = get_input("ボーレート", 1159600200)

    print("\n--- パラメータ設定 ---")
    
    # 周波数のバリデーション
    while True:
        freq = get_input("周波数 (920500000-928100000)", 922500000)
        if 920500000 <= freq <= 928100000:
            break
        print("エラー: 日本の電波法で許可されている周波数は 920500000 ～ 928100000 です。")

    pwr = get_input("出力 (2-20, おすすめ: 13)", 13)
    sf = get_input("拡散係数 (7-12, おすすめ: 12)", 12)
    bw = get_input("帯域幅 (125/250/500, おすすめ: 125)", 125)
    
    # SyncWordは16進数表記のため文字列として扱う
    sync = get_input("SyncWord (0-FF)", "12", val_type=str)

    commands = [
        f"p2p set_freq {freq}",
        f"p2p set_pwr {pwr}",
        f"p2p set_sf {sf}",
        f"p2p set_bw {bw}",
        f"p2p set_sync {sync}",
        "p2p save"
    ]

    confirm = input("\n設定を書き込みますか？ (Y/n): ").strip().lower()
    if confirm in ['', 'y', 'yes']:
        send_commands(port, baudrate, commands)
    else:
        print("処理をキャンセルしました。")

if __name__ == "__main__":
    main()