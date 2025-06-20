from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

driver = None
wait = None
initialized = False
language = "en-IN"

def init_browser():
    global driver, wait, initialized
    if initialized:
        return
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    print("Launching browser...")
    driver.get("https://realtime-stt-devs-do-code.netlify.app/")
    print("Loading website...")
    wait.until(EC.presence_of_element_located((By.ID, "language_select")))
    print("Selecting language...")

    driver.execute_script(
        f"""
        var select = document.getElementById('language_select');
        select.value = '{language}';
        var event = new Event('change');
        select.dispatchEvent(event);
        """
    )

    selected = driver.find_element(By.ID, "language_select").find_element(By.CSS_SELECTOR, "option:checked").get_attribute("value")
    if selected == language:
        print("Language selected successfully.")
    else:
        print("Error selecting language.")
    initialized = True

def stream(content: str):
    print("\033[96m\rUser Speaking: \033[93m" + f" {content}", end='', flush=True)

def get_text():
    return driver.find_element(By.ID, "convert_text").text

def SpeechRecognition() -> str:
    init_browser()

    # Start recording
    driver.find_element(By.ID, "click_to_record").click()
    wait.until(EC.presence_of_element_located((By.ID, "is_recording")))

    transcribed_text = ""
    while driver.find_element(By.ID, "is_recording").text.startswith("Recording: True"):
        current_text = get_text()
        if current_text and current_text != transcribed_text:
            transcribed_text = current_text
            stream(transcribed_text)
        time.sleep(0.1)

    transcribed_text = get_text().strip()
    
    # Clear the transcript area on the page
    driver.execute_script("document.getElementById('convert_text').textContent = '';")

    if transcribed_text:
        print("\nRecording stopped.\n")
    return transcribed_text
