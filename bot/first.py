import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from transformers import pipeline
import csv
from urllib.parse import urljoin

# Load the question-answering pipeline
tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")
model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

def extract_and_process_data(url):
   
    # add your user agent 
    # http header for request, useragent from what is my browser
    HEADERS= ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0', 'Accept-language':'en-US, en; q=0.5'})
    # The webpage URL
    # HTTP Request
    webpage = requests.get(url, headers=HEADERS)

    # Check if the request was successful
    # if webpage.status_code == 200:
    #     # Parse the HTML content
    soup = BeautifulSoup(webpage.content, "html.parser")
    # else:
    #     print("Failed to fetch the webpage.")

    def list_of_content(soup, base_url):
        result = []

        def extract_li_data(li_tag):
            li_data = {}
            a_tag = li_tag.find('a')
            if a_tag:
                li_data['text'] = a_tag.get_text(strip=True)
                relative_href = a_tag.get('href')
                if relative_href:
                    li_data['href'] = urljoin(base_url, relative_href)
                else:
                    li_data['href'] = None
            sub_ul = li_tag.find('ul')
            if sub_ul:
                li_data['sub_items'] = [extract_li_data(sub_li) for sub_li in sub_ul.find_all('li', recursive=False)]
            return li_data

        top_level_ul = soup.find('ul')
        if top_level_ul:
            top_level_li_tags = top_level_ul.find_all('li', recursive=False)
            for top_level_li in top_level_li_tags:
                li_data = extract_li_data(top_level_li)
                result.append([li_data.get('text', ''), li_data.get('href', '')])
                for sub_item in li_data.get('sub_items', []):
                    result.append([sub_item.get('text', ''), sub_item.get('href', '')])

        return result

    base_url = url
    list_of_pages = list_of_content(soup, base_url)
    # print(list_of_pages)

    csv_file_path = "each1.csv"
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(list_of_pages)

    txt_file_path= "each1text.txt"
    context=""
    context+="{"
    with open('each1text.txt', 'w', newline='') as file:
        writer = csv.writer(file)
        for item in list_of_pages:
            context+=str(item)
            writer.writerow(item)
    context+="}"
    # print(context)

    def news1(soup):
        try:
            # Find the <div> with class "padding10 bg-white m-2 homerankings"
            divs = soup.find("div", class_="padding10 bg-white m-2 homerankings")

            if divs:
                # Find the <strong> tag within the <div> to get the title
                title_tag = divs.find("strong")
                title = title_tag.get_text(strip=True) if title_tag else None

                # Find the <p> tag within the <div> to get the paragraph
                paragraph_tag = divs.find("p")
                paragraph = paragraph_tag.get_text(strip=True) if paragraph_tag else None

                return title, paragraph
            else:
                return None, None

        except Exception as e:
            # Handle exceptions if any occur
            return None, f"An error occurred: {e}"

    # ekta divas
    title, paragraph = news1(soup)
    # print(title)
    # print(paragraph)


    # Append Republic Day content to CSV file
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        context+="\n"+title+"\n"+paragraph
        csv_writer.writerow([title, paragraph])

    def get_news_and_events(soup):
        try:
            # Find all <div> elements with class 'padding10 newevents_control'
            divs = soup.find_all("div", class_="padding10 newevents_control")

            # Extract text from <h5> tags within each <div>
            h5_texts = []
            for div in divs:
                h5_tags = div.find_all("h5")
                h5_texts.extend([h5.get_text(strip=True) for h5 in h5_tags])

        except AttributeError:
            # Handle the case where elements are not found
            h5_texts = []

        return h5_texts

    # news and events of main page
    news_and_events_main = get_news_and_events(soup)
    # for text in news_and_events_main:
            # print(text,end="")
            
    # type(get_news_and_events)

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        for item in news_and_events_main:
            context+="\n"+item
            csv_writer.writerow([item])

    def get_news_update(soup):
        try:
            # Find the <marquee> tag with specific attributes
            marquee_tag = soup.find("marquee", attrs={"behavior": "alternate", "direction": "left", "style": "font-size: 16px;"})

            # Extract text from the <marquee> tag
            if marquee_tag:
                marquee_text = marquee_tag.get_text(strip=True)
                return marquee_text
            else:
                return "No <marquee> tag found with specified attributes."

        except Exception as e:
            # Handle exceptions if any occur
            return f"An error occurred: {e}"  

    # news update
    news_update = get_news_update(soup)
    # print(news_update)
    # type(news_update)

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([news_update])
        context+="\n"+news_update

    def get_announcements(soup):
        try:
            # Find all <div> elements with class 'news_content'
            news_divs = soup.find_all("div", class_='news_content')  
    #         ann_con = '\n'.join(p.get_text(strip=True) for div in news_divs for p in div.find_all("p"))
            ann_con = [p.get_text(strip=True) for div in news_divs for p in div.find_all("p")]
            
        except AttributeError:
            # Handle the case where elements are not found
            ann_con=[]
    #         ann_con = " "

        return ann_con


    announcements=get_announcements(soup)
    # print("\n".join(announcements))
    # type(announcements)


    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        for item in announcements:
            csv_writer.writerow([item])
            context+="\n"+item

    # extracting quick links
    def extract_links_in_range(soup, base_url):
        link_dict = {}

        # Find all <h4> tags with class "color_red"
        h4_tags = soup.find_all('h4', class_='color_red')

        # Iterate through each <h4> tag
        for h4_tag in h4_tags:
            # Find the <div> with class "footerlinks" within the <h4> tag
            footer_links_div = h4_tag.find_next('div', class_='footerlinks')

            # Find all <a> tags within the <div>
            a_tags = footer_links_div.find_all('a')

            # Extract link text and href and store in the dictionary
            for a_tag in a_tags:
                link_text = a_tag.get_text(strip=True)
                relative_href = a_tag.get('href')

                # Join relative href with base_url to get the full URL
                full_href = urljoin(base_url, relative_href)

                link_dict[link_text] = full_href
        
        #adding the remaning links
        # Find all <div> tags with class "col-9" within <div class="row">
        extra_divs = soup.select('div.row div.col-9')

        # Iterate through each <div> tag
        for col_9_div in extra_divs:
            # Find the parent <div class="col-xl-2 col-lg-2 col-md-2 col-sm-4 col-6"> within the <div class="col-9">
            links_div = col_9_div.find_parent('div', class_='col-xl-2 col-lg-2 col-md-2 col-sm-4 col-6')

            # Find the <a> tag within the <div class="col-xl-2 col-lg-2 col-md-2 col-sm-4 col-6">
            a_tag = links_div.find('a')

            # Extract link text and href and store in the dictionary
            if a_tag:
                link_text = col_9_div.get_text(strip=True)
                relative_href = a_tag.get('href')

                # Append to the dictionary
                link_dict[link_text] = relative_href

        return link_dict

    base_url = "https://www.griet.ac.in"  
    links_in_range = extract_links_in_range(soup, base_url)

    # print(links_in_range)

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Flatten the dictionary into a list of tuples and write to CSV
        for key, value in links_in_range.items():
            context+="\n"+key+"\n"+value
            csv_writer.writerow([key, value])

    return context


# FRONT END

st.title("Web Page Question Answering App")

user_link = st.text_input("Enter website URL:")
contextFound=""

if st.button("Enter"):
    st.spinner("please wait while its loading...")
    contextFound = extract_and_process_data(user_link)

    if contextFound:  # Check if context is not empty
        st.write("query_form")
        query = st.text_input("Ask a question about the website:")

        if st.button("Submit Query", key="submit_query"):
            # Store the user's query in session state

            # Call the qa_pipeline function with the stored query and context
            answer = qa_pipeline({'question': query, 'context': contextFound})
            st.write("pipeline function")

            # Print the answer variable for debugging
            print(answer)

            # Display the answer
            if answer:
                st.write("Answer:", answer['answer'])
            else:
                st.write("No answer found for this query.")

    else:
        st.error("The context cannot be empty. Please try again with a different URL or check the website's accessibility.")