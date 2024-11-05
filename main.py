# main.py
import streamlit as st

# メニューの選択肢を定義
menu_options = ["トップページ", "ピッキング","並び替え", "PDF作成", "在庫","追加数量","送料"]

# サイドバーでオプションメニューを表示
selected_option = st.sidebar.radio("メインメニュー", menu_options)


# 選択肢に応じて表示するページを変更
if selected_option == "トップページ":
    # トップページの内容
    st.title("トップページ")
    st.write("ようこそ！")

elif selected_option == "ピッキング":
    # pick.py の内容をインポートして実行
    from pick import picking_page
    picking_page()

elif selected_option == "並び替え":
    # pick.py の内容をインポートして実行
    from sort import main as sort_main
    sort_main()


elif selected_option == "PDF作成":
    # pdf.py の内容をインポートして実行
    from pdf import main as pdf_main
    pdf_main()

elif selected_option == "在庫":
    # Inventory.py の内容をインポートして実行
    from inventory import main as Inventory_main
    Inventory_main()


elif selected_option == "追加数量":
    # addition.py の内容をインポートして実行
    from addition import main as addition_main
    addition_main()

elif selected_option == "送料":
    # postage.py の内容をインポートして実行
    from postage import main as postage_main
    postage_main()

