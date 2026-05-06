import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# 설정123
BLOG_ID = "isanghangot"
MAX_POSTS = 3
MAX_PAGE = 20
SAVE_DIR = "naver_blog_html"

os.makedirs(SAVE_DIR, exist_ok=True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 링크 수집
def get_post_links():
    links = set()
    page = 1

    while len(links) < MAX_POSTS and page <= MAX_PAGE:
        url = f"https://blog.naver.com/PostList.naver?blogId={BLOG_ID}&currentPage={page}"
        driver.get(url)
        time.sleep(2)

        elements = driver.find_elements(By.CSS_SELECTOR, "a")

        for el in elements:
            try:
                href = el.get_attribute("href")
                if href and "logNo=" in href:
                    log_no = href.split("logNo=")[1].split("&")[0]
                    clean_url = f"https://blog.naver.com/PostView.naver?blogId={BLOG_ID}&logNo={log_no}"
                    links.add(clean_url)
            except:
                continue

        print(f"{page}페이지 / 현재 {len(links)}개 수집")
        page += 1

    return list(links)[:MAX_POSTS]

# 본문 가져오기 (핵심 수정 완료)
def get_post_content(url):
    driver.get(url)
    time.sleep(2)

    try:
        driver.switch_to.frame("mainFrame")
    except:
        pass  # 🔥 여기 중요

    soup = BeautifulSoup(driver.page_source, "html.parser")

    title_tag = (
        soup.select_one(".se-title-text span") or
        soup.select_one(".pcol1")
    )
    title = title_tag.text.strip() if title_tag else "no_title"

    content = (
        soup.select_one(".se-main-container") or
        soup.select_one("#postViewArea") or
        soup.select_one(".post-view")
    )

    html = content.prettify() if content else ""

    if not html:
        print("본문 못 찾음:", url)

    try:
        driver.switch_to.default_content()
    except:
        pass

    return title, html

# 저장
def save_html(title, html, index):
    safe_title = "".join(c for c in title if c not in r'\/:*?"<>|')
    filename = f"{index:03d}_{safe_title}.html"
    path = os.path.join(SAVE_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print("저장 완료:", filename)

# 실행
def run():
    links = get_post_links()
    print(f"\n총 {len(links)}개 링크 수집 완료\n")

    for i, link in enumerate(links):
        print(f"[{i+1}/{len(links)}] 처리중")

        title, html = get_post_content(link)

        if html:
            save_html(title, html, i)
        else:
            print("저장 스킵")

        time.sleep(1)

    driver.quit()
    print("\n모든 작업 완료")

if __name__ == "__main__":
    run()