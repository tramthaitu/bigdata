import streamlit as st
import pandas as pd
import psycopg2

conn = psycopg2.connect(
    database="postgres_db",
    user="postgres_user",
    password="postgres_password",
    host="postgres",
    port="5432"
)

# 2. Cache function để load data
@st.cache_data
def load_data_from_sql(query: str) -> pd.DataFrame:
    # pd.read_sql tự động map columns, types, trả về DataFrame
    return pd.read_sql(query, conn)

# 3. Sử dụng
df = load_data_from_sql("SELECT * FROM public.output_cb;")
df2 = load_data_from_sql("SELECT * FROM public.output_cf;")


# Làm sạch categories
df['categories'] = df['categories'].fillna("").apply(
    lambda x: ', '.join(sorted(set(cat.strip() for cat in x.split(','))))
)

# ---------- KHỞI TẠO CÁC SESSION STATE ----------
if "selected_book_id" not in st.session_state:
    st.session_state.selected_book_id = None

if "back_to_category" not in st.session_state:
    st.session_state.back_to_category = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""
    
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    
if "from_user_history" not in st.session_state:
    st.session_state.from_user_history = False
    

# ---------- GIAO DIỆN CHỌN THỂ LOẠI (vẫn nằm trong giao diện ban đầu) ----------
if not st.session_state.selected_book_id:
    name = st.text_input("Nhập tên của bạn:", value=st.session_state.user_name, key="name_input")
    if name:
        st.session_state.user_name = name
        matched_users = df2[df2['profileName'].astype(str) == name]
        if not matched_users.empty:
            st.session_state.user_id = matched_users['User_id'].values[0]
            st.session_state.from_user_history = True
        else:
            st.write("Xin chào người lạ. Hãy bắt đầu khám phá các thể loại bạn yêu thích")
            st.session_state.from_user_history = False
    # Lấy tất cả thể loại
    all_categories = sorted({
        cat.strip()
        for cats in df['categories']
        for cat in cats.split(',')
        if cat.strip()
    })

    selected_cats = st.multiselect(
        "📚 KHÁM PHÁ:",
        options=all_categories,        
        help="Lọc các sách theo thể loại đã chọn"
    )

    if selected_cats:
        def match_categories(row_categories, selected):
            row_cats = [cat.strip() for cat in str(row_categories).split(',')]
            return any(cat in row_cats for cat in selected)

        filtered_df = df[df['categories'].apply(lambda x: match_categories(x, selected_cats))]

        st.markdown(f"### 🎯 Kết quả")

        shown_books = set()
        for _, row in filtered_df.iterrows():
            book_id = row['book_id']
            if book_id in shown_books:
                continue
            shown_books.add(book_id)

            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(row['image'], width=120)
                with col2:
                    st.markdown(f"**{row['Title']}**")
                    st.markdown(f"Tác giả: {row['authors']}")
                    st.markdown(f"Thể loại: {row['categories']}")
                    st.markdown(f"Nhà xuất bản: {row['publisher']}")
                    if st.button(f"📖 Chọn sách này", key=f"book_{row['book_id']}"):
                        st.session_state.selected_book_id = row['book_id']
                        st.rerun()
        st.markdown("---")
    else:
        st.warning("Chọn ít nhất 1 thể loại.")
else:
    # ---------- GIAO DIỆN HIỆN SÁCH ĐÃ CHỌN ----------
    selected_book = df[df['book_id'].astype(str) == str(st.session_state.selected_book_id)]
    
    if selected_book.empty:
        st.error("Không tìm thấy sách đã chọn.")
    else:
        selected_book = selected_book.iloc[0]
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(selected_book['image'], width=120)
        with col2:
            st.markdown(f"**{selected_book['Title']}**")
            st.markdown(f"Tác giả: {selected_book['authors']}")
            st.markdown(f"Thể loại: {selected_book['categories']}")
            st.markdown(f"Nhà xuất bản: {selected_book['publisher']}")
            st.write(f"Mô tả: {selected_book['description']}")
        st.markdown("---")
        # ---------- GỢI Ý DỰA VÀO QUERY_ID ----------
        st.markdown("## 📚 Gợi ý sách liên quan:")
        related_books = df[
        (df['query_id'] == selected_book['book_id']) & #đang lỗi do chưa đổi df khi thực hiện chọn sách ở hai phần logic sử dụng hai df khác nhau -> phải tạo thêm code tương tự để vào từng phần khi chọn sách từ user mới và cũ
        (df['book_id'] != selected_book['book_id'])  #  loại chính nó
        ]
        if related_books.empty:
            st.warning("Không có gợi ý nào cho sách này")
        else:
            shown_books = set()
            for _, row in related_books.iterrows():
                book_id = row['book_id']
                if book_id in shown_books:
                    continue
                shown_books.add(book_id)

                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        default_image = "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9781787550360/classic-book-cover-foiled-journal-9781787550360_xlg.jpg"
                        image_url = row['image'] if isinstance(row['image'], str) and row['image'].startswith("http") else default_image
                        st.image(image_url, width=120)
                    with col2:
                        st.markdown(f"**{row['Title']}**")
                        st.markdown(f"Tác giả: {row['authors']}")
                        st.markdown(f"Thể loại: {row['categories']}")
                        st.markdown(f"Nhà xuất bản: {row['publisher']}")
                        if st.button("📖 Chọn sách này", key=f"book_{row['book_id']}"):
                            st.session_state.selected_book_id = row['book_id']
                            st.rerun()
            st.divider()
            if st.session_state.selected_book_id:
                if st.button("🔙 Quay lại chọn thể loại"):
                    st.session_state["selected_book_id"] = None
                    st.session_state.back_to_category = True
                    st.rerun()
#------------GIAO DIỆN CHO NGƯỜI DÙNG CŨ--------------
if st.session_state.from_user_history:
    st.info("Những quyển sách bạn có thể thích:")
    user_books = df2[df2['User_id'] == st.session_state.user_id]
    shown = set()
    for _, row in user_books.iterrows():
        if row["book_id"] in shown:
            continue
        shown.add(row["book_id"])
        
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                default_image = "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9781787550360/classic-book-cover-foiled-journal-9781787550360_xlg.jpg"
                image_url = row['image'] if isinstance(row['image'], str) and row['image'].startswith("http") else default_image
                st.image(image_url, width=120)
            with col2:
                st.markdown(f"**{row['Title']}**")
                st.markdown(f"Tác giả: {row['authors']}")
                st.markdown(f"Thể loại: {row['categories']}")
                st.markdown(f"Nhà xuất bản: {row['publisher']}")
                if st.button("📖 Chọn sách này", key=f"user_select_{row['book_id']}"):
                    st.session_state.selected_book_id = row['book_id']
                    st.rerun()
st.divider()
if st.session_state.selected_book_id:
    if st.button("🔙 Quay lại chọn thể loại", key="callback"):
        st.session_state["selected_book_id"] = None
        st.session_state.back_to_category = True
        st.rerun()