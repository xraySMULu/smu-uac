import requests
from bs4 import BeautifulSoup
import csv
import json
import re

def scrape():
    
    url = 'https://www.smu.edu/provost/saes/academic-support/university-advising-center/uac-staff'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    # Find all the div elements with class 'card-body'
    divs = soup.find_all('div', class_='card-body')  
    bdivs = soup.find_all('div', class_='card-footer')    
    for div in divs:
        str = div.text.strip()
        # print("Litstr:" + str)
    
        # Split the string by newline characters
        lines = str.strip().split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]

        title_str_lst = []
        name, title, email, phone = None, None, None, None
        
        num_objects = len(non_empty_lines)

        # Extract the name, title, email, and phone number from the non-empty lines
        if num_objects >= 4:
            name = non_empty_lines[0]
            email = non_empty_lines[num_objects - 2]
            phone = non_empty_lines[num_objects - 1]
        
        #clean up the data
        for i in range(len(non_empty_lines)):            
            if "advisor" in non_empty_lines[i].lower():
                title_str_lst.append(non_empty_lines[i])
                title = "-".join(title_str_lst)           

        # Create a dictionary with the extracted values
        data_dict = {
        "name": name,
        "title": title if title else non_empty_lines[1],  # Use the first line as title if no advisor found        
        "email": email,
        "phone": phone,               
        }
       
        # Convert the dictionary to a JSON string
        json_string = json.dumps(data_dict, indent=4)
        data.append(json_string)       

    csv_file_path = "output.csv"
    
    # Convert JSON strings to dictionaries
    json_to_dict = [json.loads(json_str) for json_str in data]
    
    # Get the keys (column names) from the first dictionary
    keys = json_to_dict[0].keys()
    
    # Write data to CSV file
    with open('output.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(json_to_dict)    
   
    print(f"Data written to {csv_file_path}")

if __name__ == '__main__':
    scrape()