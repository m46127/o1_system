import streamlit as st
import pandas as pd
from io import BytesIO
import chardet

# 全角数字を半角数字に変換する関数
def zenkaku_to_hankaku(s):
    zenkaku_digits = "０１２３４５６７８９"
    hankaku_digits = "0123456789"
    translation_table = str.maketrans(zenkaku_digits, hankaku_digits)
    return s.translate(translation_table)

# 都道府県ごとの送料ルールを定義
shipping_rules = {
    '福岡県,佐賀県,大分県,長崎県,熊本県,宮崎県,鹿児島県,沖縄県': {5: 500, 10: 630, 20: 880, 30: 1930, 50: 2350},
    '徳島県,香川県,高知県,愛媛県': {5: 500, 10: 730, 20: 980, 30: 2030, 50: 2600},
    '岡山県,広島県,鳥取県,島根県,山口県': {5: 500, 10: 730, 20: 980, 30: 1930, 50: 2450},
    '京都府,滋賀県,奈良県,大阪府,兵庫県,和歌山県': {5: 500, 10: 730, 20: 980, 30: 2030, 50: 2700},
    '富山県,石川県,福井県': {5: 500, 10: 930, 20: 1180, 30: 2130, 50: 2950},
    '静岡県,愛知県,岐阜県,三重県': {5: 500, 10: 930, 20: 1180, 30: 2130, 50: 2900},
    '長野県,新潟県': {5: 500, 10: 930, 20: 1180, 30: 2330, 50: 3250},
    '東京都,神奈川県,千葉県,埼玉県,茨城県,群馬県,山梨県,栃木県': {5: 500, 10: 1030, 20: 1280, 30: 2330, 50: 3350},
    '宮城県,山形県,福島県': {5: 500, 10: 1230, 20: 1480, 30: 2530, 50: 3700},
    '青森県,秋田県,岩手県': {5: 500, 10: 1230, 20: 1480, 30: 2530, 50: 4150},
    '北海道,札幌,道東,道南,道央,道北,道西': {5: 500, 10: 1330, 20: 1580, 30: 2930, 50: 4900},
}

# 送料計算関数
def calculate_shipping(row):
    prefecture = row['着店県名称'].strip()
    weight_columns = ['明細１重量', '明細２重量', '明細３重量', '明細４重量', '明細５重量', '明細６重量', '明細７重量', '明細８重量']
    quantity_columns = ['明細１個数', '明細２個数', '明細３個数', '明細４個数', '明細５個数', '明細６個数', '明細７個数', '明細８個数']


    # その他の都道府県は通常の送料計算
    total_shipping = 0
    for weight_col, qty_col in zip(weight_columns, quantity_columns):
        weight = zenkaku_to_hankaku(str(row.get(weight_col, 0))).strip()
        quantity = zenkaku_to_hankaku(str(row.get(qty_col, 0))).strip()

        try:
            weight = float(weight)
            quantity = int(quantity)
        except ValueError:
            continue

        rule_applied = False
        for region, rates in shipping_rules.items():
            if prefecture in region.split(','):
                for max_weight, rate in sorted(rates.items()):
                    if weight <= max_weight:
                        total_shipping += rate * quantity
                        rule_applied = True
                        break
                if rule_applied:
                    break

    return total_shipping

def main():
    st.title("送料集計システム")

    # CSVファイルのアップロード
    uploaded_file = st.file_uploader("CSVファイルを選択してください", type="csv")

    if uploaded_file is not None:
        # ファイルのエンコーディングを検出
        raw_data = uploaded_file.read()
        detected_encoding = chardet.detect(raw_data)['encoding']
        st.write(f"検出されたエンコーディング: {detected_encoding}")

        # ファイルを適切なエンコーディングで読み込む
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file, encoding=detected_encoding)
            st.write("データの最初の数行:", df.head())
        except Exception as e:
            st.error(f"ファイルの読み込みに失敗しました: {e}")
            return

        # 送料を計算して新しい列に追加
        df['送料'] = df.apply(calculate_shipping, axis=1)
        df['送料（消費税込）'] = df['送料'] * 1.1

        # 送料と消費税込み送料の合計を表示
        total_shipping = df['送料'].sum()
        total_shipping_with_tax = df['送料（消費税込）'].sum()
        st.write(f"送料の合計: {total_shipping}円")
        st.write(f"送料の合計（消費税込）: {total_shipping_with_tax:.0f}円")

        # 結果をExcelでダウンロード
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='送料計算結果')
        output.seek(0)

        st.download_button(
            label="計算結果をエクセルでダウンロード",
            data=output,
            file_name='shipping_calculations_with_tax.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    main()
