import streamlit as st
import pandas as pd

# 全角数字を半角数字に変換する関数
def zenkaku_to_hankaku(s):
    zenkaku_digits = "０１２３４５６７８９"
    hankaku_digits = "0123456789"
    translation_table = str.maketrans(zenkaku_digits, hankaku_digits)
    return s.translate(translation_table)

# 都道府県ごとの送料ルールを定義
shipping_rules = {
    '福岡県,佐賀県,大分県,長崎県,熊本県,宮崎県,鹿児島県': {5: 500, 10: 630, 20: 880, 30: 1930, 50: 2350},
    '徳島県,香川県,高知県,愛媛県': {5: 500, 10: 730, 20: 980, 30: 2030, 50: 2600},
    '岡山県,広島県,鳥取県,島根県,山口県': {5: 500, 10: 730, 20: 980, 30: 1930, 50: 2450},
    '京都府,滋賀県,奈良県,大阪府,兵庫県,和歌山県': {5: 500, 10: 730, 20: 980, 30: 2030, 50: 2700},
    '富山県,石川県,福井県': {5: 500, 10: 930, 20: 1180, 30: 2130, 50: 2950},
    '静岡県,愛知県,岐阜県,三重県': {5: 500, 10: 930, 20: 1180, 30: 2130, 50: 2900},
    '長野県,新潟県': {5: 500, 10: 930, 20: 1180, 30: 2330, 50: 3250},
    '東京都,神奈川県,千葉県,埼玉県,茨城県,群馬県,山梨県,栃木県': {5: 500, 10: 1030, 20: 1280, 30: 2330, 50: 3350},
    '宮城県,山形県,福島県': {5: 500, 10: 1230, 20: 1480, 30: 2530, 50: 3700},
    '青森県,秋田県,岩手県': {5: 500, 10: 1230, 20: 1480, 30: 2530, 50: 4150},
    '北海道': {5: 500, 10: 1330, 20: 1580, 30: 2930, 50: 4900},
}

# 送料計算関数
def calculate_shipping(row):
    # 行から都道府県、重量、個数を取得し、全角数字を半角に変換
    prefecture = row['着店県名称']
    weight = zenkaku_to_hankaku(str(row['明細１重量']))
    quantity = zenkaku_to_hankaku(str(row['明細１個数']))

    # 数値に変換
    try:
        weight = float(weight)
        quantity = int(quantity)
    except ValueError:
        return 0  # 数値に変換できない場合は送料0円

    # デバッグ用の出力
    st.write(f"Processing: {prefecture}, {weight}, {quantity}")

    # 沖縄の場合の特別処理
    if prefecture == '沖縄県':
        shipping_fee = row['明細運賃V'] * 0.1
        return shipping_fee * quantity

    # ルールに基づき送料を計算
    for region, rates in shipping_rules.items():
        if prefecture in region.split(','):
            for max_weight, rate in sorted(rates.items()):
                if weight <= max_weight:
                    return rate * quantity  # 該当する送料に「明細1個数」を掛ける
    
    # 5kg以下の場合は500円
    if weight <= 5:
        return 500 * quantity
    
    return 0  # 該当しない場合は送料0円

def main():
    st.title("送料集計システム")

    # CSVファイルのアップロード
    uploaded_file = st.file_uploader("CSVファイルを選択してください", type="csv")
    
    if uploaded_file is not None:
        # CSVファイルをデータフレームとして読み込む（Shift_JISエンコーディングで）
        df = pd.read_csv(uploaded_file, encoding='shift_jis')

        # データを表示（オプション）
        st.write(df.head())

        # 送料を計算して新しい列に追加
        df['送料'] = df.apply(calculate_shipping, axis=1)

        # 送料の合計を表示
        total_shipping = df['送料'].sum()
        st.write(f"送料の合計: {total_shipping}円")

        # 計算結果をダウンロード可能なCSVファイルとして保存
        csv = df.to_csv(index=False, encoding='shift_jis')
        st.download_button(label="計算結果をダウンロード", data=csv, file_name='shipping_calculations.csv', mime='text/csv')

if __name__ == "__main__":
    main()