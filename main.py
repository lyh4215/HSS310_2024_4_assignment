from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.common.alert import Alert
from time import sleep
import random

# User-Agent 리스트
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
]
# ChromeDriver 경로 설정
driver_path = "C:/chromedriver/chromedriver.exe"

# Chrome 옵션 설정
options = Options()
options.add_argument("--start-maximized")  # 브라우저 창 최대화
options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
#options.add_argument("--headless=new")
# Service 객체 생성
service = Service(driver_path)

# WebDriver 초기화
driver = webdriver.Chrome(service=service, options=options)

# WebDriver 탐지 우회
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
    """
})

# 쿠팡 상품 URL
url = "https://www.coupang.com/vp/products/6091182064?vendorItemId=78633105451"

# 웹사이트 열기
driver.get(url)

# 페이지 로딩 대기
wait = WebDriverWait(driver, 10)
sleep(3)
# 상품평 탭 클릭

# try:
#     # 리뷰 탭 클릭 대기
#     review_tab = driver.find_element(By.XPATH, '//li[contains(text(), "상품평")]')
#     review_tab.click()

# except UnexpectedAlertPresentException:
#     # 팝업(Alert) 처리
#     try:
#         alert = Alert(driver)
#         print("Alert 텍스트:", alert.text)
#         alert.accept()  # 팝업 확인 클릭
#     except NoAlertPresentException:
#         print("팝업이 없습니다.")
# 데이터 저장용 리스트
reviews = []
# 페이지 수집 루프
current_page = 1
ask = input("리뷰를 수집하시겠습니까? (y/n): ")
while True:
    try:
        # 리뷰 요소 가져오기
        review_elements = driver.find_elements(By.CSS_SELECTOR, "article.sdp-review__article__list.js_reviewArticleReviewList")
        
        for review in review_elements:
            try:
                # 날짜와 별점 가져오기
                date = review.find_element(By.CLASS_NAME, "sdp-review__article__list__info__product-info__reg-date").text
                star = review.find_element(By.CLASS_NAME, "sdp-review__article__list__info__product-info__star-orange").get_attribute("data-rating")
                reviews.append({"Date": date, "Star": star})
            except Exception as e:
                print("리뷰 수집 중 오류 발생:", e)

        active_button = driver.find_element(By.CSS_SELECTOR, ".sdp-review__article__page__num--active")
        current_page = int(active_button.get_attribute("data-page"))
        print(f"현재 페이지: {current_page}")

        if current_page % 10 == 0:
            print("10단위 페이지입니다. Next 버튼을 클릭합니다.")
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".sdp-review__article__page__next--active"))
                )
                next_button.click()
                current_page += 1
                print(f"Next 버튼을 눌러 {current_page}페이지로 이동합니다.")
                time.sleep(random.uniform(2, 5))
                continue
            except Exception as e:
                print("Next 버튼 클릭 중 오류:", e)
                break

        # 모든 페이지 번호 버튼 가져오기
        page_buttons = driver.find_elements(By.CSS_SELECTOR, ".sdp-review__article__page__num")
        next_page_button = None

        # 다음 페이지 버튼 탐색
        for button in page_buttons:
            page_number = int(button.get_attribute("data-page"))
            if page_number == current_page + 1:  # 다음 페이지 번호
                next_page_button = button
                break

        # 다음 페이지 버튼이 없으면 종료
        if next_page_button is None:
            print("다음 페이지 버튼을 찾을 수 없습니다. 마지막 페이지입니다.")
            break

        # 다음 페이지 버튼 클릭
        next_page_button.click()
        current_page += 1
        print(f"{current_page}페이지로 이동")

        # 페이지 로딩 대기
        time.sleep(random.uniform(1, 5)) 
    except Exception as e:
        print("페이지 탐색 중 오류 발생:", e)
        break

# 웹 드라이버 닫기
driver.quit()

# 데이터프레임 생성 및 저장
df = pd.DataFrame(reviews)
df.to_csv("coupang_reviews.csv", index=False, encoding="utf-8-sig")

print("데이터가 coupang_reviews.csv 파일로 저장되었습니다.")