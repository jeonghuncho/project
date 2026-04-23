import time
import os
import base64

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ==========================
# 설정
# ==========================
BLOG_ID = "metivna"
MAX_POSTS = 1
MAX_PAGE = 30
SAVE_DIR = "naver_blog_pdf"

os.makedirs(SAVE_DIR, exist_ok=True)

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ==========================
# 링크 수집
# ==========================
def get_post_links():
    links = set()
    page = 1

    while len(links) < MAX_POSTS and page <= MAX_PAGE:
        url = f"https://blog.naver.com/PostList.naver?blogId={BLOG_ID}&currentPage={page}"
        driver.get(url)
        time.sleep(2)

        elements = driver.find_elements("css selector", "a")

        for el in elements:
            try:
                href = el.get_attribute("href")
                if href and "logNo=" in href:
                    log_no = href.split("logNo=")[1].split("&")[0]
                    clean_url = f"https://blog.naver.com/PostView.naver?blogId={BLOG_ID}&logNo={log_no}"
                    links.add(clean_url)
            except:
                continue

        print(f"{page}페이지 / {len(links)}개")
        page += 1

    return list(links)[:MAX_POSTS]

# ==========================
# PDF 저장 (화면 그대로)
# ==========================
def save_pdf(url, index):
    driver.get(url)
    time.sleep(3)

    try:
        driver.switch_to.frame("mainFrame")
        time.sleep(1)
    except:
        pass

    pdf = driver.execute_cdp_cmd("Page.printToPDF", {
        "printBackground": True,
        "preferCSSPageSize": True
    })

    filename = os.path.join(SAVE_DIR, f"{index:03d}.pdf")

    with open(filename, "wb") as f:
        f.write(base64.b64decode(pdf['data']))

    print("PDF 저장:", filename)

    try:
        driver.switch_to.default_content()
    except:
        pass

# ==========================
# 실행
# ==========================
def run():
    links = get_post_links()
    print(f"\n총 {len(links)}개\n")

    for i, link in enumerate(links):
        print(f"[{i+1}/{len(links)}]")

        try:
            save_pdf(link, i)
        except Exception as e:
            print("실패:", e)

        time.sleep(2)

    driver.quit()
    print("완료")

if __name__ == "__main__":
    run()