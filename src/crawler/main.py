import requests
from bs4 import BeautifulSoup

def crawl_sendo_products(base_url, num_pages=1):
    """
    Crawl product data from Sendo.vn.
    
    Args:
        base_url (str): The URL of the Sendo page to scrape.
        num_pages (int): Number of pages to scrape.
    
    Returns:
        list: A list of dictionaries containing product data.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    product_data = []
    
    for page in range(1, num_pages + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}: {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Update the selector based on the website's structure
        products = soup.find_all("div", class_="product-item")
        
        for product in products:
            try:
                name = product.find("div", class_="product-name").text.strip()
                price = product.find("span", class_="product-price").text.strip()
                link = product.find("a", class_="product-link")["href"]
                
                product_data.append({
                    "name": name,
                    "price": price,
                    "link": link
                })
            except AttributeError:
                # Skip products with missing data
                continue
    
    return product_data

if __name__ == "__main__":
    base_url = "https://www.sendo.vn/san-pham"  # Update with a valid product listing URL
    num_pages = 5  # Number of pages to scrape
    
    data = crawl_sendo_products(base_url, num_pages)
    
    for item in data:
        print(item)
