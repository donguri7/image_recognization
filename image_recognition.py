from google.cloud import vision
import io
import os

# Google Cloud vision client init
client = vision.ImageAnnotatorClient()

def detect_text(path):
    """画像からテキストを検出する"""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
        
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    # print('Texts:')
    # for text in texts:
    #     print(f'\n"{text.description}"')
        
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message)
        )
    
    return response

def extract_product_names(text):
    lines = text.split('\n')
    product_names = []
    current_product = ""
    for line in lines:
        line = line.strip() # 空白文字の削除
        if '小計' in line:
            break # 商品リストの終わり
        
        # 商品行の開始を示す特徴
        if '#' in line and '¥' in line:
            if current_product:
                product_names.append(current_product.strip())
            current_product = line.split('#')[-1].split('¥')[0].strip() # '#'と価格を除去(万代)
            if current_product.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                current_product = current_product[2:].strip() # 先頭の数字を削除
        elif 'F:' in line or 'ソ#' in line:
            # 特殊なフォーマットの商品行
            if current_product:
                product_names.append(current_product.strip())
            current_product = line.split(':')[-1].split('¥')[0].strip()
        elif current_product and not line.startswith('¥') and '個' not in line:
            # 前の行の続きの可能性がある商品名
            current_product += ' ' + line
            
    if current_product:
        product_names.append(current_product.strip())
        
    # クリーンアップ
    cleaned_products = []
    for name in product_names:
        name = name.split('個')[0].strip()
        name = name.replace('■', '').strip()
        name = name.split('#')[0].strip()  # '#' 以降を削除
        name = name.split('ソ')[0].strip()  # 'ソ' 以降を削除
        if name:
            cleaned_products.append(name)
            
    return cleaned_products

image_path = '/Users/takumi.i/Desktop/画像認識/mandai.jpeg'

response = detect_text(image_path)
# print('1')

texts = response.text_annotations
# print('2')
if texts:
    full_text = texts[0].description
    # print('3')
    product_names = extract_product_names(full_text)
    # print('4')
    print("\nExtracted Product Names:")
    for name in product_names:
        print(name)
