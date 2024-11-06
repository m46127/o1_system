import streamlit as st
import pandas as pd
import base64
from io import BytesIO

def calculate_additional_quantity(sku_quantity):
    """
    商品数量に基づき、追加数量を計算
    5点: +1, 6点: +2、以降1点増えるごとに+1
    """
    if sku_quantity >= 5:
        return sku_quantity - 4  # 5点で+1、6点で+2、7点で+3
    else:
        return 0  # 4点以下の場合は追加数量なし

def process_file(uploaded_file):
    df = pd.read_csv(uploaded_file)  # CSVファイルを読み込み
    header = list(df.columns)  # ヘッダーを保存
    result = []
    
    # SKUの条件を複数設定
    valid_sku_prefixes = ['dear-esc-1', 'dear-mcl-1', 'dear-fwa-1', 'dear-mlo-1', 'dear-des-1', 'dear-full-1']

    for _, row in df.iterrows():
        total_sku_quantity = 0
        
        # SKU1〜SKU10から、SKUが指定された条件で始まるものを探す
        for i in range(10):
            sku_col = f'SKU{i+1}'
            qty_col = f'商品数量{i+1}'
            
            if sku_col in row and qty_col in row:
                sku = row[sku_col]
                quantity = row[qty_col]
                
                # 複数条件に一致するSKUをカウント
                if pd.notna(sku) and any(sku.startswith(prefix) for prefix in valid_sku_prefixes):
                    total_sku_quantity += quantity
        
        # 追加数量の計算
        additional_quantity = calculate_additional_quantity(total_sku_quantity)
        
        # 行に追加数量を含めて結果リストに追加
        row_with_additional = row.tolist() + [total_sku_quantity, additional_quantity]
        result.append(row_with_additional)
    
    # 新しい列を追加したデータフレームを作成
    new_columns = header + ['指定されたSKUの総数量', '追加数量']
    result_df = pd.DataFrame(result, columns=new_columns)
    
    return result_df

def download_link_excel(df, filename='output.xlsx'):
    # DataFrameをExcel形式でバイナリに変換
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)

    # エンコードしてダウンロードリンクを作成
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel File</a>'
    return href

def main():
    st.title("SKU 集計と追加数量の計算")

    # ファイルアップローダー
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # ファイル処理
        result_df = process_file(uploaded_file)
        
        if result_df is not None:
            # 追加数量の合計を計算して表示
            total_additional_quantity = result_df['追加数量'].sum()
            st.write(f"追加数量の合計: {total_additional_quantity}")
            
            # 結果を表示
            st.dataframe(result_df)
            
            # ダウンロードリンクを表示
            st.markdown(download_link_excel(result_df), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
