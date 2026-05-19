from PIL import Image, ImageDraw

def create_icon():
    # 256x256の透明な背景の画像を作成
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景の円（LoRaをイメージした少し落ち着いたブルー）
    draw.ellipse((16, 16, 240, 240), fill=(41, 128, 185))

    # アンテナのタワー部分（白）
    draw.polygon([(110, 200), (146, 200), (133, 100), (123, 100)], fill=(255, 255, 255))
    draw.ellipse((118, 80, 138, 100), fill=(255, 255, 255))

    # 電波の波紋（外側）
    draw.arc((60, 60, 196, 196), start=210, end=330, fill=(255, 255, 255), width=12)
    # 電波の波紋（内側）
    draw.arc((90, 90, 166, 166), start=210, end=330, fill=(255, 255, 255), width=12)

    # ICOフォーマットで保存
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    print("icon.ico を生成しました。")

if __name__ == "__main__":
    create_icon()