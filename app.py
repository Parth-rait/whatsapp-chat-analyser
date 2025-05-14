import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout='wide')
st.title("📱 WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("Choose a chat text file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    # 🔍 Display first 500 characters of raw chat text
    st.text("----- RAW CHAT PREVIEW -----")
    st.text(data[:500])  # This helps us debug the format

    # Call the preprocessing function
    df = preprocessor.preprocess(data)

    # Stop execution if DataFrame is empty
    if df.empty:
        st.error("❌ Could not parse any messages. Your chat format may not match the expected pattern.")
        st.stop()


    st.sidebar.title("Analysis")

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.header("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Shared", num_media)
        col4.metric("Links Shared", num_links)

        # Monthly Timeline
        st.header("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.header("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='blue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Maps
        st.header("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.subheader("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Heatmap
        user_heatmap = helper.activity_heatmap(selected_user, df)
        if not user_heatmap.empty:
            st.title("Weekly Activity Heatmap")
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap, ax=ax)
            st.pyplot(fig)
        else:
            st.warning("No data available to show heatmap.")

        # Most Busy Users
        if selected_user == 'Overall':
            st.header("Most Active Users")
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            ax.bar(x.index, x.values, color='red')
            st.pyplot(fig)
            st.dataframe(new_df)

        # WordCloud
        st.header("WordCloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most Common Words
        st.header("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        st.dataframe(most_common_df)

        # Emoji Analysis
        st.header("Emoji Usage")
        emoji_df = helper.emoji_helper(selected_user, df)
        st.dataframe(emoji_df)
