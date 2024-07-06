from google.cloud import vision
import io
import os
import json

# Google Cloud vision client init
client = vision.ImageAnnotatorClient()

def detect_text(path):
    """画像からテキストを検出する"""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
        
    image = vision.Image(content=content) # 画像
    response = client.text_detection(image=image) # 画像からテキスト検出
    texts = response.text_annotations # テキスト注釈を代入
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message)
        )
    
    return response

def extract_lines(text):
    return [line.strip() for line in text.split('\n') if line.strip()] # 空の行、各行の先頭と末尾の空白文字を削除、テキストを改行文字で分割

# 画像ファイルのパス
image_path = '/Users/takumi.i/Desktop/image_recog/Images/mandai2.jpeg'

# 出力JSONファイルのパスを生成
output_path = os.path.splitext(image_path.replace('/Images', '/Raws'))[0] +'.json'

response = detect_text(image_path)

texts = response.text_annotations # description:文字 vertices:位置情報格納

if texts:
    full_text = texts[0].description
    lines = extract_lines(full_text)
    
    # JSONファイルに保存
    output_data = {
        "lines": lines
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"テキストの各行をJSONファイルに保存しました: {output_path}")
    
    # 内容を表示
    print("\n保存された内容:")
    for line in lines:
        print(line)
else:
    print("テキストが検出されませんでした。")