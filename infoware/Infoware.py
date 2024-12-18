import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from bs4 import BeautifulSoup

# Set up the webdriver
driver_path = "C:\\Windows\\chromedriver.exe"  # Update with your path to ChromeDriver
options = Options()
options.headless = False  # Set to False to see the browser (for debugging)
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Function to authenticate with a custom login page
def login_to_amazon(username, password, login_url):
    driver.get(login_url)
    wait = WebDriverWait(driver, 10)

    # Enter username
    email_field = wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))
    email_field.send_keys(username)

    # Click continue
    continue_button = driver.find_element(By.ID, 'continue')
    continue_button.click()

    # Enter password
    password_field = wait.until(EC.presence_of_element_located((By.ID, 'ap_password')))
    password_field.send_keys(password)

    # Click sign-in button
    sign_in_button = driver.find_element(By.ID, 'signInSubmit')
    sign_in_button.click()

    # Check if login was successful
    try:
        wait.until(EC.presence_of_element_located((By.ID, 'nav-link-accountList')))
        print("Login successful.")
    except:
        print("Login failed.")

# Function to scrape product data
def scrape_amazon_category(category_url, max_products=1500):
    driver.get(category_url)
    all_products = []
    category_name = category_url.split("/")[-2]  # Extract dynamic category name

    while True:
        try:
            # Wait for the product grid to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p13n-desktop-grid")))

            # Locate the product grid
            product_column = driver.find_element(By.CLASS_NAME, "p13n-desktop-grid")
            soup = BeautifulSoup(product_column.get_attribute('innerHTML'), 'html.parser')

            # Find all products
            products = soup.find_all('div', {'class': 'p13n-grid-content'})
            print(f"Found {len(products)} products on the page.")

            for product in products:
                try:
                    # Extract product details
                    name = product.find('div', {'class': '_cDEzb_p13n-sc-css-line-clamp-3_g3dy1'})
                    name = name.text.strip() if name else 'N/A'

                    price = product.find('span', {'class': '_cDEzb_p13n-sc-price_3mJ9Z'})
                    price = price.text.strip() if price else 'N/A'

                    discount = product.find('span', {'class': 'a-color-price'})
                    discount = discount.text.strip() if discount else 'N/A'

                    best_seller_rating = product.find('span', {'class': 'a-icon-alt'})
                    best_seller_rating = best_seller_rating.text.strip() if best_seller_rating else 'N/A'

                    ship_from = product.find('span', {'class': 'a-size-small a-color-secondary'})
                    ship_from = ship_from.text.strip() if ship_from else 'N/A'

                    seller = product.find('div', {'class': '_cDEzb_p13n-sc-byline_1gL4V'})
                    seller = seller.text.strip() if seller else 'N/A'

                    rating = product.find('span', {'class': 'a-icon-alt'})
                    rating = rating.text.strip() if rating else 'N/A'

                    description = product.find('div', {'class': '_cDEzb_p13n-sc-css-line-clamp-3_g3dy1'})
                    description = description.text.strip() if description else 'N/A'

                    number_bought = product.find('span', {'class': 'a-size-small a-color-secondary'})
                    number_bought = number_bought.text.strip() if number_bought else 'N/A'

                    # Find all images
                    images = product.find_all('img')
                    image_links = [img['src'] for img in images if 'src' in img.attrs]

                    # Criteria: Product must have a discount and be a bestseller
                    try:
                        cleaned_discount = ''.join(filter(str.isdigit, discount))  # Removes non-digit characters
                        discount_percentage = int(cleaned_discount) if cleaned_discount else 0

                        if discount_percentage > 50:
                            all_products.append({
                                'Product Name': name,
                                'Product Price': price,
                                'Sale Discount': discount,
                                'Best Seller Rating': best_seller_rating,
                                'Ship From': ship_from,
                                'Sold By': seller,
                                'Rating': rating,
                                'Product Description': description,
                                'Number Bought in the Past Month': number_bought,
                                'Category Name': category_name,
                                'All Available Images': image_links,
                            })

                        # Stop if we have collected the desired number of products
                        if len(all_products) >= max_products:
                            return all_products

                    except Exception as e:
                        print(f"Error processing discount: {e}")
                        continue

                except Exception as e:
                    print(f"Error extracting product details: {e}")
                    continue

            # Check for "Next" button
            try:
                next_page = driver.find_element(By.CSS_SELECTOR, '.s-pagination-next')
                if 'a-disabled' in next_page.get_attribute('class'):
                    print("No more pages available.")
                    break
                print("Navigating to the next page...")
                next_page.click()
                time.sleep(2)
            except Exception:
                print("No more pages available.")
                break

        except Exception as e:
            print(f"Error during scraping: {e}")
            break

    print(f"Scraped {len(all_products)} products from category: {category_url}")
    return all_products

# Main function
def main():
    # Replace with your Amazon login credentials
    amazon_username = 'mohdakram6174@gmail.com'
    amazon_password = 'Akram@1299'
    login_url = 'https://www.amazon.in/ap/signin?openid.pape.preferred_auth_policies=SinglefactorWithPossessionChallenge&openid.pape.max_auth_age=900&openid.return_to=https%3A%2F%2Fwww.amazon.in%2Fap%2Fcnep%3Fie%3DUTF8%26orig_return_to%3Dhttps%253A%252F%252Fwww.amazon.in%252Fyour-account%26openid.assoc_handle%3Dinflex%26pageId%3Dinflex&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0'

    login_to_amazon(amazon_username, amazon_password, login_url)

    categories = [
        'https://www.amazon.in/gp/bestsellers/kitchen',
        'https://www.amazon.in/gp/bestsellers/shoes',
        'https://www.amazon.in/gp/bestsellers/computers',
        'https://www.amazon.in/gp/bestsellers/electronics',
        'https://www.amazon.in/gp/bestsellers/toys-and-games',
        'https://www.amazon.in/gp/bestsellers/books',
        'https://www.amazon.in/gp/bestsellers/clothing-and-accessories',
        'https://www.amazon.in/gp/bestsellers/watches',
        'https://www.amazon.in/gp/bestsellers/beauty',
        'https://www.amazon.in/gp/bestsellers/sports-and-fitness'
    ]

    all_data = []
    for url in categories:
        print(f"Scraping category: {url}")
        category_data = scrape_amazon_category(url)
        all_data.extend(category_data)

    # Store data into a CSV file
    output_file = os.path.join(os.getcwd(), 'amazon_best_sellers.csv')
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Scraping complete. Data saved to '{output_file}'.")
    driver.quit()

if __name__ == "__main__":
    main()
