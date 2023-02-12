import streamlit as st
from streamlit_chat import message
import pandas as pd

from utils import get_most_similar_content
from scraper import collect_data, collect_reviews, get_response

st.title("Amazon Question Answering System.")

with st.form("form"):
    url = st.text_input("Label enter the URL of the page you have queries about?")
    submit = st.form_submit_button(label="Lessgo!!!")

df_reviews = collect_reviews(url)
df_data = collect_data(get_response(url))

df = pd.concat([df_data, df_reviews])

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def get_text():
    input_text = st.text_input("You: ", "Hello, how are you?", key="input")
    return input_text

user_input = get_text()

if user_input:
    query = user_input
    results = get_most_similar_content(df, query, top_k=2)

    documents = []
    for result in results:
        documents.append(result['doc'])

    output = question_answering(documents, query)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)


if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i)+'_user')
