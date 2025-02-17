import streamlit as st
import pandas as pd
import requests
import csv
from PIL import Image
import io
from scraper import *

st.markdown(
    """
    <style>
    /* Target the image container rendered by st.image */
    .stImage > div > img {
        height: 100px !important;
        object-fit: contain;  /* ensures the image is contained without distortion */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

actions = {
    "duapune": duaPune,
    "karriera.al": karrieraAl,
    "njoftime.al": njoftimePuneAl,
    "gjirafa": GjirafaPune,
    "profesionist": ProfesionistiAl
}

def fetch_data_from_url(url):
    for key, func in actions.items():
        if key in url:
            data=func(url)
            return data


def list_to_csv(data_list):
    output = io.StringIO()
    writer = csv.writer(output, delimiter="~")  # Use "~" as the delimiter

    for item in data_list:
        writer.writerow(item.split("~"))  # Split each row by "~" and write to CSV

    return output.getvalue()

def get_company_image(company_name):
    company_images = {
        "Dua Pune": "images/duaPune.png",
        "Anegino": "images/anegino.png",
        "EPPC": "images/eppc.png",
        "Karriera": "images/karriera.png",
        "Profesionisti": "images/profesionisti.png",
        "Puna Juaj": "images/punaJuaj.png"
    }
    return company_images.get(company_name, "images/default_logo.png")


def resize_image(image_path, height=100):
    image = Image.open(image_path)
    aspect_ratio = image.width / image.height
    width = int(aspect_ratio * height)
    resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
    return resized_image


def is_valid_url(url):
    try:
        #response = requests.get(url)
        #response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


companies = ["Dua Pune", "Anegino", "EPPC", "Karriera", "Profesionisti", "Puna Juaj"]

st.title("Job Portal Data Aggregator")

url_input = st.text_area("Enter the job portal URL:", "")

if st.button("Fetch Data"):
    if url_input:
        if is_valid_url(url_input):
            raw_data = fetch_data_from_url(url_input)
            if raw_data:
                csv_content = list_to_csv(raw_data)
                st.download_button(
                    label="Download CSV",
                    data=csv_content,
                    file_name="output.csv",
                    mime="text/csv"
                )
        else:
            st.error("The URL is not valid. Please try another!")
    else:
        st.warning("Please enter a URL!")

st.write("\n\n")
cols = st.columns(len(companies))

for i, company in enumerate(companies):
    image_path = get_company_image(company)
    resized_image = resize_image(image_path, height=100)
    cols[i].image(resized_image, caption=company)
