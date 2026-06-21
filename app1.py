import os

import google.generativeai as genai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def get_csv_text(csv_file):
    text_parts = []
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        row_text = " ".join(str(value) for value in row if pd.notna(value))
        if row_text:
            text_parts.append(row_text)
    return " ".join(text_parts)


def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return splitter.split_text(text)


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():
    prompt_template = """
Answer the question as detailed as possible from the provided context. If the
answer is not available in the context, say "answer is not available in the
context" and do not make up an answer.

Context:
{context}

Question:
{question}

Answer:
"""

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)


def answer_question(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )
    docs = vector_store.similarity_search(user_question)
    chain = get_conversational_chain()
    return chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True,
    )


def main():
    st.set_page_config(page_title="CollegeDataBot")
    st.header("CollegeDataBot")

    if not GOOGLE_API_KEY:
        st.warning("Set GOOGLE_API_KEY in your environment or .env file before processing data.")

    user_question = st.text_input("Ask a question from the uploaded college CSV")
    if user_question:
        if not os.path.exists("faiss_index"):
            st.info("Upload and process a CSV before asking questions.")
        else:
            response = answer_question(user_question)
            st.write("Reply:", response["output_text"])

    with st.sidebar:
        csv_file = st.file_uploader("Upload a CSV file", type=["csv"])
        if st.button("Submit & Process"):
            if csv_file is None:
                st.warning("Please upload a CSV file first.")
            elif not GOOGLE_API_KEY:
                st.error("GOOGLE_API_KEY is not set.")
            else:
                with st.spinner("Processing..."):
                    raw_text = get_csv_text(csv_file)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("Done")


if __name__ == "__main__":
    main()
