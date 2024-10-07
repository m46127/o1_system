import streamlit as st
import pandas as pd
import base64
from io import BytesIO

def calculate_additional_quantity(a_sku_quantity):
    """
    商品数量に基づき、追加数量を計算
    4点: +1, 5点: +2, 6点: +3、以降1点増えるごとに+1
    """
    if a_sku_quantity >= 4:
        return a_sku_quantity - 3  # 4点で+1、5点で+2、6点で+3
    else:
        return 0  # 3点以下の場合は追加数量なし

def process_file(uploaded_file):
    df = pd.read_csv(uploaded_file)  # CSVファイルを読み込み
    header = list(df.columns)  # ヘッダーを保存
    result = []
    
    for _, row in df.iterrows():
        total_a_sku_quantity = 0
        
        # SKU1〜SKU10から、SKUがAで始まるものを探す
        for i in range(10):  # SKU1〜SKU10までを処理
            sku_col = f'SKU{i+1}'
            qty_col = f'商品数量{i+1}'
            
            if sku_col in row and qty_col in row:
                sku = row[sku_col]
                quantity = row[qty_col]
                
                if pd.notna(sku) and sku.startswith('A'):  # SKUがAで始まるかチェック
                    total_a_sku_quantity += quantity
        
        # 追加数量の計算
        additional_quantity = calculate_additional_quantity(total_a_sku_quantity)
        
        # 行に追加数量を含めて結果リストに追加
        row_with_additional = row.tolist() + [total_a_sku_quantity, additional_quantity]
        result.append(row_with_additional)
    
    # 新しい列を追加したデータフレームを作成
    new_columns = header + ['Aから始まるSKUの総数量', '追加数量']
    result_df = pd.DataFrame(result, columns=new_columns)
    
    return result_df

def download_link(df, filename='output.csv'):
    # DataFrameをCSV形式でバイナリに変換
    output = BytesIO()
    df.to_csv(output, index=False)
    
    # エンコードしてダウンロードリンクを作成
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

def main():
    st.title("SKU 集計と追加数量の計算")

    # ファイルアップローダー
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # ファイル処理
        result_df = process_file(uploaded_file)
        
        if result_df is not None:
            # 結果を表示
            st.dataframe(result_df)
            
            # ダウンロードリンクを表示
            st.markdown(download_link(result_df), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
