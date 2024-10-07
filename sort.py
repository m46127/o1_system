import streamlit as st
import pandas as pd
import base64
from io import StringIO

def consumer_to_group_label(consumer):
    product_codes = sorted(list(consumer["products"].keys()))
    return ",".join(product_codes)

def process_file(uploaded_file):
    # CSVファイルを読み込む
    df = pd.read_csv(uploaded_file)
    header = list(df.columns)  # ヘッダーを保存
    consumers = []
    
    for _, row in df.iterrows():
        consumer = {"row": row.tolist()}
        products = {}
        for i in range(10):  # SKU1〜SKU10までを処理
            sku_col = f'SKU{i+1}'
            qty_col = f'商品数量{i+1}'
            if sku_col in row and qty_col in row:
                product_code = row[sku_col]
                amount = row[qty_col]
                if pd.notna(product_code) and pd.notna(amount):
                    # 整数として処理するためにint()を使用
                    products[product_code] = int(amount) + products.get(product_code, 0)
        consumer["products"] = products
        consumers.append(consumer)
    
    # 商品情報でグループ化
    consumer_groups = {}
    for consumer in consumers:
        label = consumer_to_group_label(consumer)
        l = consumer_groups.get(label, [])
        l.append(consumer)
        consumer_groups[label] = l
    
    # グループを並び替え
    sorted_consumer_groups = sorted(consumer_groups.values(), key=lambda x: len(x), reverse=True)
    output = []
    for consumers in sorted_consumer_groups:
        for consumer in consumers:
            output.append(consumer["row"])
    
    # ソート済みデータを返す
    return header, output

def write_to_csv(header, output):
    # DataFrameとしてヘッダーとデータを作成
    df = pd.DataFrame(output, columns=header)
    
    # CSVファイルのバイナリを作成
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    return csv_output.getvalue()

def main():
    st.title("CSV File Processor")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        header, output = process_file(uploaded_file)
        csv_data = write_to_csv(header, output)
        
        # ダウンロードリンクを作成
        b64 = base64.b64encode(csv_data.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="sorted_output.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
