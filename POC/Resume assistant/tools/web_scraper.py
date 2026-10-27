import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_job_description(url: str) -> str:
    try:
        # Setup headless Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(3)  # Let the page load

        # Wait for JD container (customize XPath if needed)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]'))
            )
        except Exception as wait_err:
            logging.warning(f"XPath wait failed: {wait_err}")

        soup = BeautifulSoup(driver.page_source, "lxml")

        # Try to find JD content
        content_data = soup.find("div", class_=lambda x: x and "dang-inner-html" in x)

        if content_data:
            jd_text = content_data.get_text(separator="\n", strip=True)
        else:
            jd_text = soup.get_text(separator="\n", strip=True)

        driver.quit()

        # Clean and validate
        jd_text = "\n".join([line.strip() for line in jd_text.splitlines() if line.strip()])
        logging.info(f"Scraped JD text (first 500 chars):\n{jd_text[:500]}")

        if not jd_text.strip():
            raise ValueError("Job description scraping returned empty content")

        return jd_text[:5000]

    except Exception as e:
        logging.error(f"JD scraping error: {e}")
        return "Job description scraping failed. Please check the URL or try pasting the text instead."
