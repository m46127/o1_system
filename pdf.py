import streamlit as st
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfgen import canvas
import pandas as pd
import os
import shutil
from PyPDF2 import PdfMerger, PdfReader
import glob
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

w, h = portrait(A4)

def adjust_font_size(text, font_name, max_width, cv):
    """
    テキストの長さに応じてフォントサイズを調整する関数。
    """
    font_size = 10  # 基本のフォントサイズ
    text_width = cv.stringWidth(text, font_name, font_size)
    
    # 文字幅が最大幅を超えた場合、フォントサイズを縮小
    if text_width > max_width:
        font_size = font_size * (max_width / text_width)
    
    return font_size

def create_pdf_files(uploaded_file):
    pdfmetrics.registerFont(TTFont('mmt', './fonts/GenShinGothic-Monospace-Medium.ttf'))
    output_files = []
    
    # output フォルダをクリーンアップ
    if os.path.exists('output'):
        shutil.rmtree('output')
    os.makedirs('output', exist_ok=True)
    
    # ファイルが空でないか確認
    uploaded_file.seek(0)
    if len(uploaded_file.read()) == 0:
        print("エラー: アップロードされたファイルが空です")
        return
    
    # ファイルをデータフレームに変換し、NaNを空文字列に置き換える
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file)  # CSVファイルを読み込む
    df = df.fillna('')  # NaNを空文字列に置き換える

    for index, record in df.iterrows():
        # ファイルの指定
        output_file = f'./output/output_{index+1}.pdf'  # 完成したPDFの保存先
        output_files.append(output_file)
        
        # キャンバスの設定
        cv = canvas.Canvas(output_file, pagesize=(w, h))
        cv.setFillColorRGB(0, 0, 0)
        cv.setFont('mmt', 12)

        # 顧客情報の描画
        customer_id = record.get('顧客ID', '')  # 列が存在しない場合は空文字列を使用
        cv.setFont('mmt', 10) 
        cv.drawString(30, h - 120, f"顧客ID:{customer_id}")
        cv.drawString(30, h - 60, '納品書')
        cv.setFont('mmt', 12) 
        cv.drawString(30, h - 80, 'この度はお買い上げいただき、ありがとうございます。')
        
        # 住所情報の描画（存在しない列は空文字列）
        o_todokede_saki_1 = record.get('お届け先名称1', '')
        o_todokede_saki_2 = record.get('お届け先名称2', '')
        o_todokede_yubin = record.get('お届け先郵便番号', '')
        o_todokede_jusho_1 = record.get('お届け先住所1', '')
        o_todokede_jusho_2 = record.get('お届け先住所2', '')
        o_todokede_jusho_3 = record.get('お届け先住所3', '')

        # 「お届け先名称1」の文字サイズ調整
        max_width_1 = 200  # 最大表示幅
        adjusted_font_size_1 = adjust_font_size(f"{o_todokede_saki_1}様", 'mmt', max_width_1, cv)
        cv.setFont('mmt', adjusted_font_size_1)
        cv.drawString(30, h - 140, f"{o_todokede_saki_1}様")

        
        
        # その他の情報
        cv.setFont('mmt', 10)  # 通常のフォントサイズに戻す
        cv.drawString(30, h - 155, f"〒{o_todokede_yubin}")
        cv.drawString(30, h - 170, str(o_todokede_jusho_1))
        cv.drawString(30, h - 185, str(o_todokede_jusho_2))
        cv.drawString(30, h - 200, str(o_todokede_jusho_3))

        # ご依頼主情報の描画
        go_irainushi_name = record.get('ご依頼主名称1', '')
        go_irainushi_yubin = record.get('ご依頼主郵便番号', '')
        go_irainushi_jusho_1 = record.get('ご依頼主住所1', '')
        go_irainushi_jusho_2 = record.get('ご依頼主住所2', '')

        cv.setFont('mmt', 10)
        cv.drawString(350, h - 140, go_irainushi_name)
        cv.drawString(350, h - 155, f"〒{go_irainushi_yubin}")
        cv.drawString(350, h - 170, go_irainushi_jusho_1)
        cv.drawString(350, h - 185, go_irainushi_jusho_2)

        # 商品リストの描画
        items = get_items(record)
        x_start = 30  # 表の左上のX座標
        y_start = h - 250  # 表の左上のY座標
        table_width = 540  # 表の幅
        table_height = 20 * len(items)  # 表の高さ (1行あたり20の高さを仮定)
        
        cv.setFont('mmt', 8)

        # ヘッダー行の描画
        header_height = 20  # ヘッダーの高さ
        cv.setFillColor(colors.lightgrey)  # ヘッダーの背景色を灰色に設定
        cv.rect(x_start, y_start, table_width, header_height, stroke=0, fill=1)  # 背景色を塗りつぶす
        cv.setFillColor(colors.black)  # テキストの色を黒に戻す

        # ヘッダーのテキストを描画
        cv.drawString(x_start + 10, y_start + 5, "SKU")
        cv.drawString(x_start + 110, y_start + 5, "商品名")
        cv.drawString(x_start + 310, y_start + 5, "商品数量")

        # 枠線の描画
        cv.rect(x_start, y_start - table_height, table_width, table_height + 20)  # 全体の枠
        for i in range(len(items) + 1):  # 行ごとの枠
            cv.line(x_start, y_start - 20 * i, x_start + table_width, y_start - 20 * i)

        cv.line(x_start + 100, y_start, x_start + 100, y_start - table_height)  # SKUと商品名の間の縦線
        cv.line(x_start + 300, y_start, x_start + 300, y_start - table_height)  # 商品名と数量の間の縦線

        # 各商品の描画
        for i, item in enumerate(items):
            cv.drawString(x_start + 10, y_start - 20 * (i + 1) + 5, str(item['code']))
            cv.drawString(x_start + 110, y_start - 20 * (i + 1) + 5, item['name'])
            cv.drawString(x_start + 310, y_start - 20 * (i + 1) + 5, str(int(item['count'])))

        # PDFの保存
        cv.showPage()
        cv.save()
    return output_files

def get_items(record):
    items_dict = {}
    for i in range(30):
        sku_col = f'SKU{i + 1}'
        name_col = f'商品名{i + 1}'
        count_col = f'商品数量{i + 1}'

        # 列が存在するか確認してから値を取得
        code = record.get(sku_col, None)
        name = record.get(name_col, None)
        count = record.get(count_col, None)

        if code and pd.notna(code):  # 商品コードが空でない場合
            if code not in items_dict:
                item = {
                    'code': code,
                    'name': name if pd.notna(name) else '',
                    'count': int(count) if pd.notna(count) else 0,  # 数量を整数型に変換
                }
                items_dict[code] = item
            else:
                items_dict[code]['count'] += int(count) if pd.notna(count) else 0

    items = list(items_dict.values())
    return items

def merge_pdf_in_dir(dir_path, dst_path):
    l = glob.glob(os.path.join(dir_path, 'output_*.pdf'))
    l.sort()

    merger = PdfMerger()
    for p in l:
        if not PdfReader(p).is_encrypted:
            merger.append(p)

    merger.write(dst_path)
    merger.close()

def main():
    st.title('PDF生成システム')
    uploaded_file = st.file_uploader("CSVファイルを選択してください", type="csv")  # CSVファイルを選択できるように変更
    if uploaded_file is not None:
        output_files = create_pdf_files(uploaded_file)
        merged_file = './output/merged.pdf'
        merge_pdf_in_dir('output', merged_file)

        with open(merged_file, "rb") as f:
            st.download_button(
                label="PDFをダウンロード",
                data=f,
                file_name="merged.pdf",
                mime="application/pdf",
            )

# main関数を実行
if __name__ == "__main__":
    main()
