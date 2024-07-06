import json
import re
import os

def clean_item_name(item):
    # 一般的なクリーニングルール
    item = re.sub(r'[#♯]\d+', '', item)
    item = re.sub(r'¥\d+(\s*x\s*\d+)?', '', item)
    item = re.sub(r'@\d+(\s*x\s*\d+)?', '', item)
    item = re.sub(r'\d+個', '', item)
    item = re.sub(r'^[リF♯]:?\s*', '', item)  # '♯' も削除
    item = re.sub(r'\s*#\d+$', '', item)
    item = re.sub(r'\s+', ' ', item)
    return item.strip()

def is_valid_item(item):
    invalid_patterns = [
        '#」', '-', 'リ#', 'R0035', '軽減税率', 'バイオマスレジ袋', '値引', '商品代金',
        r'^\d{4}年\d{1,2}月\d{1,2}日',  # 日付パターン
        r'\d{1,2}:\d{2}',  # 時間パターン
        r'^[#♯]\d+$',  # '#08' や '♯08' のパターン
        r'^\*\d+$',  # '*542' のパターン
        r'^,\d+\)$',  # ',475)' のパターン
    ]
    return (len(item) > 1 and 
            not any(re.search(pattern, item) for pattern in invalid_patterns) and
            not item.isdigit())

def normalize_item_name(item):
    item = re.sub(r'(\d+)ml', r'\1mL', item)
    item = re.sub(r'(\d+)L', r'\1L', item)
    item = re.sub(r'\s', '', item)
    return item

def extract_items(lines):
    items = []
    start_flag = False
    end_flag = False
    for line in lines:
        # 商品リストの開始を検出
        if re.search(r'領収書|明細|商品名', line):
            start_flag = True
            continue
        
        # 商品リストの終了を検出
        if re.search(r'小計|合計|税|お預り', line):
            end_flag = True
        
        if start_flag and not end_flag:
            item = clean_item_name(line)
            if is_valid_item(item):
                items.append(normalize_item_name(item))
    
    return items

def process_receipt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return extract_items(data['lines'])

def main():
    input_dir = "Raws"
    files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    all_items = []
    
    for file in files:
        file_path = os.path.join(input_dir, file)
        items = process_receipt(file_path)
        all_items.extend(items)
        print(f"\n商品名 from {file}:")
        for item in items:
            print(item)
    
    unique_items = sorted(set(all_items))
    
    output_dir = "Outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'extracted_items.json')
    output = {"商品名": unique_items}
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n全ての商品名を '{output_file}' に保存しました。")
    print(f"抽出された商品数: {len(unique_items)}")

if __name__ == "__main__":
    main()