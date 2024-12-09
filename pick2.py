import streamlit as st
import pandas as pd
from io import BytesIO

def add_group_numbers(df):
    """
    グループ番号をデータフレームに追加します。
    """
    # グループ化に必要なカラムを取得
    group_labels = []
    for _, row in df.iterrows():
        # SKUカラムを取得してソート
        skus = [row[f'SKU{i+1}'] for i in range(10) if pd.notna(row.get(f'SKU{i+1}'))]
        group_label = ",".join(sorted(skus))  # ソートしたSKUを結合してラベル化
        group_labels.append(group_label)

    # グループ番号を生成
    df['グループ番号'] = pd.factorize(group_labels)[0] + 1  # グループ番号を1からスタート
    return df

def process_picking_list(df):
    """
    ピッキングリストをグループごとに集計し、詳細なリストを横並び形式で作成します。
    """
    grouped_details = []

    for group_num, group_df in df.groupby("グループ番号"):  # グループ番号でデータを分ける
        # 横並び形式でデータを準備
        group_row = {
            "グループ番号": group_num,
            "件数": len(group_df),  # グループ内の行数
            "ページ番号開始": group_df.index.min() + 1,
            "ページ番号終了": group_df.index.max() + 1
        }
        sku_index = 1  # SKUのインデックスを管理

        sku_details = {}
        for _, row in group_df.iterrows():
            for i in range(10):  # SKU1〜SKU10まで
                sku_col = f"SKU{i+1}"
                name_col = f"商品名{i+1}"
                qty_col = f"商品数量{i+1}"

                if sku_col in row and pd.notna(row[sku_col]):
                    sku = row[sku_col]
                    name = row[name_col] if name_col in row else ""
                    qty = row[qty_col] if qty_col in row and pd.notna(row[qty_col]) else 0

                    if sku not in sku_details:
                        sku_details[sku] = {"name": name, "quantity": int(qty)}
                    else:
                        sku_details[sku]["quantity"] += int(qty)  # 購入数量を加算

        # 横並びの形式に展開
        for sku, details in sku_details.items():
            group_row[f"SKU{sku_index}"] = sku
            group_row[f"商品名{sku_index}"] = details["name"]
            group_row[f"商品数量{sku_index}"] = details["quantity"]  # SKUごとの購入数量を表示
            sku_index += 1

        grouped_details.append(group_row)

    return pd.DataFrame(grouped_details)

def picking2_page():
    st.title("細分化ピッキングリスト")

    uploaded_file = st.file_uploader("CSVファイルを選択してください", type="csv")

    if uploaded_file is not None:
        # アップロードされたCSVを読み込む
        df = pd.read_csv(uploaded_file)

        # グループ番号を追加
        df_with_groups = add_group_numbers(df)

        # グループ番号での集計（横並び形式）
        grouped_details = process_picking_list(df_with_groups)

        # DataFrameを表示
        st.dataframe(grouped_details)

        # ダウンロード用にExcelファイルを準備
        excel_stream = BytesIO()
        grouped_details.to_excel(excel_stream, index=False, sheet_name="ピッキングリスト")
        excel_stream.seek(0)

        st.download_button(
            label="ピッキングリストをダウンロード",
            data=excel_stream,
            file_name="detailed_picking_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    picking2_page()
