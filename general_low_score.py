import json
import re
import os

def clean_item_name(item):
    # 価格、数量、その他の不要な情報を削除
    item = re.sub(r'¥\d+(\s*x\s*\d+)?', '', item)
    item = re.sub(r'@\d+(\s*x\s*\d+)?', '', item)
    item = re.sub(r'\d+個', '', item)
    item = re.sub(r'^[#リF]:?\s*\d*\s*', '', item)  # '#12 ' や 'F: ' などを削除
    item = re.sub(r'\s*#\d+$', '', item)
    return item.strip()

def is_valid_item(item):
    invalid_starts = ['#」', '-', 'リ#', 'R0035']
    return (len(item) > 1 and 
            not item.startswith(tuple(invalid_starts)) and
            not item.isdigit() and
            '軽減税率' not in item and
            'バイオマスレジ袋' not in item)

def normalize_item_name(item):
    # 商品名の正規化（例：容量情報の統一）
    item = re.sub(r'(\d+)ml', r'\1mL', item)
    item = re.sub(r'(\d+)L', r'\1L', item)
    return item

def extract_items_mandai(lines):
    items = []
    for line in lines:
        if '#' in line or line.startswith('リ#') or line.startswith('F:') or '#' in line:
            item = clean_item_name(line)
            # '#' と数字を削除
            item = re.sub(r'^#?\d+\s*', '', item)
            if '#' in line:
                item = re.sub(r'\s', '', item)
                item = re.sub(r'#\d+', '', item)
            if is_valid_item(item):
                items.append(normalize_item_name(item))
    return items

def extract_items_711(lines):
    items = []
    start_extracting = False
    skip_next = False
    for i, line in enumerate(lines):
        if '領収書' in line or '領収証' in line:
            start_extracting = True
            continue
        if not start_extracting:
            continue
        if skip_next:
            skip_next = False
            continue
        if '@' in line or '*' in line or '値引額' in line:
            skip_next = True
            continue
        if not line.startswith('(') and not line.isdigit() and '¥' not in line and ':' not in line:
            item = clean_item_name(line)
            if is_valid_item(item):
                items.append(normalize_item_name(item))
            # 次の行も確認して、商品名が2行に分かれている可能性を考慮
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if not next_line.startswith('(') and not next_line.isdigit() and '¥' not in next_line and ':' not in next_line:
                    combined_item = item + ' ' + clean_item_name(next_line)
                    if is_valid_item(combined_item):
                        items.append(normalize_item_name(combined_item))
        if '合計' in line:
            break
    return items

def extract_items(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if 'mandai' in file_path:
        return extract_items_mandai(data['lines'])
    elif '711' in file_path:
        return extract_items_711(data['lines'])
    else:
        return []
    
def main():
    # 入力ファイルのディレクトリを "Raws" に変更
    input_dir = "Raws"
    files = ['mandai.json', 'mandai2.json', '711_2.json', '711.json']
    all_items = []
    
    for file in files:
        file_path = os.path.join(input_dir, file)
        items = extract_items(file_path)
        all_items.extend(items)
        print(f"\n商品名 from {file}:")
        for item in items:
            print(item)
            
    # 重複を削除して全商品名をソート
    unique_items = sorted(set(all_items))
    
    # 出力ディレクトリを作成（存在しない場合）
    output_dir = "Outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # 結果をJSONファイルに保存（"Outputs" ディレクトリ内）
    output_file = os.path.join(output_dir, 'extracted_items.json')
    output = {"商品名": unique_items}
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"\n全ての商品名を '{output_file}' に保存しました。")
    print(f"抽出された商品数: {len(unique_items)}")
    
if __name__ == "__main__":
    main()