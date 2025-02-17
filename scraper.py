from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, re
import requests
from bs4 import BeautifulSoup
import time
import csv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def duaPune(main_url):
    job_links = []
    url=main_url+"&page="
    count=1
    page_no=1

    while count>0:
        " ""Fetch job links from the main job listing page." ""
        page_url=url+str(page_no)
        response = requests.get(page_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch job listings: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        element = soup.find("a", class_="apply-job")

        if element:
            page_no=page_no+1
            for link in soup.select(".apply-job"):  
                job_url = link.get("href")
                if job_url and not job_url.startswith("http"):
                    job_url = page_url + job_url  
                job_links.append(duapune_job_data(job_url))
        else:
            count=0
    
    return job_links

def duapune_job_data(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch job listings: {response.status_code}")
        return " "
        
    soup = BeautifulSoup(response.text, "html.parser")

    titulli=str(str(soup.find("h1", class_=url).text.strip()))
    kategoria=str(soup.find("span", class_="main-jobs-tag").find("a").get_text(strip=True))

    p_elements = soup.find("div", class_="side-right").find_all("p")
    tipi = p_elements[1].get_text(strip=True)
    paga = p_elements[5].get_text(strip=True)

    d_elements = soup.find("div", class_="job-details").find_all("div", class_="main-content-description")
    pershkrimi = d_elements[1].get_text(separator=" ", strip=True) if len(d_elements) > 1 else " "
    kerkesat = d_elements[3].get_text(separator=" ", strip=True) if len(d_elements) > 3 else " "

    company = str(soup.find("h3", class_="c-name").text.strip())

    return titulli+"~"+kategoria+"~"+company+"~"+tipi+"~"+paga+"~Dua Pune~"+url+"~01/01/1001"+"~"+pershkrimi+"~"+kerkesat+"~"+url

def karrieraAl(main_url):
    job_links = []
    url = main_url + "?faqe="
    base_url = "https://karriera.al"
    page_no = 1  

    while True:
        page_url = url + str(page_no)
        response = requests.get(page_url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch job listings: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="table")
        
        if not table:
            print("No table found, stopping.")
            break

        rows = table.find_all("tr")
        if len(rows) <= 2: 
            print("No job listings found, stopping.")
            break

        for row in rows:
            a_tag = row.find("a", href=True)
            if a_tag:
                job_url = a_tag.get("href")
                if job_url and not job_url.startswith("http"):
                    job_url = base_url + job_url
                job_links.append(karrieraAl_job_data(job_url))
        
        page_no =page_no+ 1  

    return job_links

def karrieraAl_job_data(main_url):
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")
    company = soup.find("div", class_="job-txt").find("h5").text.strip()
    
    divs=soup.find("div", class_="job-inside").find_all("div")
    titulli = divs[1].find("span").text.strip()
    kategoria = divs[2].find("span").text.strip()
    tipi = divs[3].find("span").text.strip()
    paga = "--"
    pershkrimi = divs[4].get_text(separator=" ", strip=True) if len(divs) > 1 else " "
    kerkesat =divs[5].get_text(separator=" ", strip=True) if len(divs) > 1 else " "
    
    return titulli + "~" + kategoria + "~" + company + "~" + tipi + "~" + paga + "~Karriera Al~" +  "~01/01/1001" + "~" + pershkrimi + "~" + kerkesat+"~"+main_url

def njoftimePuneAl(url):
    main_url = clear_page_number(url)
    counter = 1
    jobs = []

    while True:
        response = requests.get(main_url + str(counter), headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch job listings: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        spanet = soup.find_all("span", class_="salary")

        if spanet:
            for span in spanet:
                linku = span.find("a")["href"] if span.find("a") else ""
                salary = span.find("strong").get_text(strip=True) if span.find("strong") else ""
                butoni_txt=span.find("a").get_text(strip=True)
                tipi = span.get_text(strip=True, separator=" ").replace(salary, "").replace(butoni_txt,"").strip()

                if linku and salary:
                    jobs.append(njoftimePuneAl_all_data(linku, salary, tipi))

            counter += 1
        else:
            break

    return jobs

def njoftimePuneAl_all_data(linku, salary, j_type):
    response = requests.get(linku)
    soup = BeautifulSoup(response.text, "html.parser")
    company = " "
    divs=soup.find("div", class_="inner-box").find_all("div", recursive=False)
    titulli = soup.find("div", class_="inner-box").find("h2").get_text(strip=True, separator=" ").replace("Ndaje", "")
    kategoria = " "
    tipi = j_type
    paga = salary
    pershkrimi = divs[-1].get_text(separator=" ", strip=True) if divs else " "
    kerkesat =" "
    return titulli + "~" + kategoria + "~" + company + "~" + tipi + "~" + paga + "~NjoftimePune Al~" +  "~01/01/1001" + "~" + pershkrimi + "~" + kerkesat+"~"+linku

def clear_page_number(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Set 'page' to an empty string instead of removing it
    if "page" in query_params:
        query_params["page"] = [""]

    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    
    return new_url

def GjirafaPune(main_url):
    job_links = []
    base_url="https://gjirafa.com/Top/Pune?"
    url_params=extract_query_part(main_url)
    page_no=0

    while True:
        " ""Fetch job links from the main job listing page." ""
        page_url=base_url+"f="+str(page_no)+"&"+url_params
        response = requests.get(page_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch job listings: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        element = soup.find("ul", class_="noresultsList")
        if element!=None:
            break
        else:
            page_no=page_no+1
            for link in soup.find_all("div", class_="pun_Img"):  
                job_url = link.get("id")
                if job_url and not job_url.startswith("http"):
                    job_url = page_url + job_url  
                job_links.append(gjirafaPune_all_data(job_url))

    return job_links

def gjirafaPune_all_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    divs=soup.find_all("div", class_="gjc1 v-pd-tb")
    div1=divs[0].find_all("h3")
    tipi=div1[0].get_text(strip=True)
    kategoria=div1[1].get_text(strip=True)

    company=soup.find("div", id="contact-panel").find_all("h3")[1].get_text(strip=True)
    titulli=soup.find("h2", class_="primeAdsTitle").get_text(strip=True)

    kerkesat=""
    pershkrimi=divs[2].get_text(separator=" ", strip=True)
    paga=""
    data=""
    div2=divs[1].find_all("div", class_="display-field")
    if len(div2)==1:
        data=div2[0].get_text(strip=True)
    else:
        paga=div2[0].get_text(strip=True)
        data=div2[1].get_text(strip=True)

    return titulli + "~" + kategoria + "~" + company + "~" + tipi + "~" + paga + "~Gjirafa Pune~" +  data + "~" + pershkrimi + "~" + kerkesat+"~"+url

def extract_query_part(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Check if 'f' exists in the query string
    if 'f' in query_params:
        # Extract everything after 'f=value' and '&'
        remaining_query = parsed_url.query.split(f"f={query_params['f'][0]}&", 1)
        return remaining_query[1] if len(remaining_query) > 1 else ''
    
    # If 'f' does not exist, extract everything after 'Pune?'
    query = '&'.join(f"{key}={value[0]}" for key, value in query_params.items())
    return query
    
def extract_query_part_Profesionisti(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    # Check if 'page' exists in the query string
    if 'page' in query_params:
        # Extract everything after 'page=value' and '&'
        remaining_query = parsed_url.query.split(f"page={query_params['page'][0]}&", 1)
        return remaining_query[1] if len(remaining_query) > 1 else ''
    
    # If 'page' does not exist, extract everything after
    query = '&'.join(f"{key}={value[0]}" for key, value in query_params.items())
    return query
    
def ProfesionistiAl(page_link):
    job_links = []
    base_url="https://profesionist.al/?"
    main_url="https://profesionist.al"
    url_params=extract_query_part_Profesionisti(page_link)
    page_no=1
    
    while True:
        " ""Fetch job links from the main job listing page." ""
        page_url=base_url+"page="+str(page_no)+"&"+url_params
        response = requests.get(page_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch job listings: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        a_tag = soup.find('a', string=lambda text: text and text.strip() == "Faqja tjetër »")
        if a_tag==None and page_no!=1:
            break
        else:
            page_no=page_no+1
            for link in soup.find_all('a', href=lambda href: href and "/njoftim-pune/" in href):  
                job_url = link.get("href")
                titulli=link.find_all("div", recursive=False)[0].find("h2").get_text(strip=True)
                company=link.find_all("div", recursive=False)[0].find("p").get_text(strip=True)
                tipi=link.find_all("div", class_="flex items-center text-gray-600 text-sm")[1].get_text(strip=True)
                paga=link.find_all("div", class_="flex items-center text-gray-600 text-sm")[2].get_text(strip=True)

                if job_url and not job_url.startswith("http"):
                    job_url = main_url + job_url  
                job_links.append(profesionistiAl_job_data(job_url, tipi, company, titulli, paga))
    
    return job_links

def profesionistiAl_job_data(url, tipi, company, titulli, paga):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    divet=soup.find("div", class_="max-w-full mx-auto bg-white sm:border sm:border-gray-300 sm:rounded-lg sm:shadow-md p-6").find_all("div", recursive=False)
    kategoria=divet[3].find_all("div", recursive=False)[-1].find_all("p")[-1].get_text(strip=True)
    data=""
    pershkrimi=divet[-3].get_text(separator=" ", strip=True)
    kerkesat=divet[-2].get_text(separator=" ", strip=True)

    return titulli + "~" + kategoria + "~" + company + "~" + tipi + "~" + paga + "~Profesionisti Al~" +  data + "~" + pershkrimi + "~" + kerkesat+"~"+url