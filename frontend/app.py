import streamlit as st
import requests

st.title("要件定義書作成アシスタント")

st.write("プロジェクトの要件を自動で分析・整理し、要件定義書を作成します。")

user_request = st.text_area(
    "プロジェクトの概要を入力してください",
    height=200,
    placeholder="例: オンライン予約システムを作りたい。ユーザーは予約日時を選択でき、管理者は予約状況を確認できるようにしたい。"
)

if st.button("要件定義書を作成"):
    if user_request:
        with st.spinner("要件定義書を作成中..."):
            try:
                response = requests.post(
                    "http://localhost:8000/generate_requirements",
                    json={"request": user_request}
                )
                if response.status_code == 200:
                    requirements_doc = response.json()["requirements_doc"]
                    st.success("要件定義書が作成されました！")
                    st.text_area("作成された要件定義書", value=requirements_doc, height=400)
                else:
                    st.error("エラーが発生しました。もう一度お試しください。")
            except requests.exceptions.ConnectionError:
                st.error("バックエンドサーバーに接続できません。サーバーが起動していることを確認してください。")
    else:
        st.warning("プロジェクトの概要を入力してください。")
