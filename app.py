import os
import streamlit as st
import pickle
import numpy as np

# Set layout to wide
st.set_page_config(layout="wide")


# Load data
def load_data():
    popular_df = pickle.load(open("artifacts/popular.pkl", "rb"))
    book_pivot_table = pickle.load(open("artifacts/book_pivot_table.pkl", "rb"))
    books = pickle.load(open("artifacts/books.pkl", "rb"))
    similarity_scores = pickle.load(open("artifacts/similarity_scores.pkl", "rb"))
    return popular_df, book_pivot_table, books, similarity_scores


popular_df, book_pivot_table, books, similarity_scores = load_data()


# Streamlit app
st.markdown(
    "<h1 style='text-align: center; color: solid White;'>ShowMyBooks2.O : Book Recommender System</h1>",
    unsafe_allow_html=True,
)

# st.markdown(
#     "<h1 style='text-align: center; color: white;'>ShowMyBooks2.O : <a href='https://showmybooks.onrender.com' target='_blank'>Book Recommender System</a></h1>",
#     unsafe_allow_html=True,
# )


with st.container():
    # Navigation
    page = st.sidebar.selectbox(
        "**Choose a Category**", ["Popular Books", "Recommendations"]
    )

    # Settings
    st.sidebar.title("Customizations")
    books_per_row = st.sidebar.slider(
        "Adjust the number of books per row", min_value=1, max_value=10, value=4
    )
    num_recommendations = st.sidebar.slider(
        "How many recommendations do you want?", min_value=1, max_value=10, value=4
    )
    width = st.sidebar.slider(
        "Adjust the width of screen ", min_value=800, max_value=1920, value=1200
    )
    # Add port number section
    st.sidebar.title("Port Settings")
    port_number = st.sidebar.slider(
        "Adjust the port number",
        min_value=8000,
        max_value=9000,
        value=8501,
    )

    border_color_options = st.sidebar.color_picker("Choose a frame color ")

    # Calculate image width based on selected width
    image_width = width // books_per_row

    def get_markdown_style(border_color_options):
        return f"""
        <style>
        .book-container {{
            border: 1px solid {border_color_options};
            padding: 10px;
            width: {image_width}px;
            margin-bottom: 10px;
        }}
        </style>
        """

    background_color = st.sidebar.color_picker("Choose a background color")

    # Website Link
    st.sidebar.title("Explore More")
    st.sidebar.markdown(
        "<a href='https://showmybooks.onrender.com'><button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px;'>ShowMyBooks</button></a>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <style>
    .stApp {{
        background-color: {background_color};
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    markdown_style = get_markdown_style(border_color_options)

    def recommend_books(user_input):
        try:
            # Check if the user_input exists in the index
            if user_input not in book_pivot_table.index:
                return "Book not found in index."

            # Index fetch
            index = np.where(book_pivot_table.index == user_input)[0]

            # Check if index is empty
            if len(index) == 0:
                return "Pivot table operation failed due to empty data."

            index = index[0]
            similar_items = sorted(
                list(enumerate(similarity_scores[index])),
                key=lambda x: x[1],
                reverse=True,
            )[1 : num_recommendations + 1]

            data = []
            for i in similar_items:
                if i[0] < len(book_pivot_table.index):
                    item = []
                    temp_df = books[books["Book-Title"] == book_pivot_table.index[i[0]]]
                    item.extend(
                        list(temp_df.drop_duplicates("Book-Title")["Book-Title"].values)
                    )
                    item.extend(
                        list(
                            temp_df.drop_duplicates("Book-Title")["Book-Author"].values
                        )
                    )
                    item.extend(
                        list(
                            temp_df.drop_duplicates("Book-Title")["Image-URL-M"].values
                        )
                    )
                    data.append(item)
            return data
        except Exception as e:
            return str(e)

        # Popular books section

    if page == "Popular Books":
        st.header("Reader's Choice : Top 50 Books")
        # st.write("Top 50 Books:")
        for i in range(0, 50, books_per_row):
            cols = st.columns(books_per_row)
            for j, col in enumerate(cols):
                if i + j < 50:
                    with col:
                        st.markdown(markdown_style, unsafe_allow_html=True)
                        st.markdown(
                            f"""
                        <div class="book-container">
                        <img src="{popular_df.iloc[i + j]['Image-URL-M']}" width="{width}">
                        **{popular_df.iloc[i + j]['Book-Title']}**
                        <br>
                        Author: {popular_df.iloc[i + j]['Book-Author']}
                        <br>
                        Votes: {popular_df.iloc[i + j]['num_ratings']}
                        <br>
                        Rating: {round(popular_df.iloc[i + j]['avg_ratings'], 3)}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

    elif page == "Recommendations":
        # Recommendation page
        st.title("Book Suggestions")
        user_input = st.selectbox("*Your Reading List Awaits*", book_pivot_table.index)
        if st.button("Recommend"):
            # Recommendation logic
            data = recommend_books(user_input)
            if isinstance(data, str):
                st.write(data)
            else:
                # Display recommended books
                st.subheader(f"Top {num_recommendations} Recommended books for you:")
                cols = st.columns(num_recommendations)
                for i, col in enumerate(cols):
                    if i < len(data) and i < num_recommendations:
                        with col:
                            st.markdown(markdown_style, unsafe_allow_html=True)
                            st.markdown(
                                f"""
                            <div class="book-container">        
                            <img src='{data[i][2]}' width='{image_width}' height='300'><br>
                            **{data[i][0]}**<br>
                            Author: {data[i][1]}<br>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

st.run(port=port_number)
