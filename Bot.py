import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from colorama import init, Fore

init(autoreset=True)

class Bot:
    def __init__(self):
        self.clear_screen()
        self.initialize_driver()
        self.setup_service_xpaths()
        self.service_wait_times = { # Custom wait times for each service with bounds
            "followers": (125, 135),
            "hearts": (125, 135),
            "comment_hearts": (125, 135),
            "views": (125, 135),
            "shares": (85, 100),
            "favorites": (125, 135),
        }

    def clear_screen(self): # Escape sequence to clear the screen
        print("\033c", end="")

    def initialize_driver(self): # Set up Chrome options for WebDriver, including user agent and logging level
        print(Fore.YELLOW + "[~] Loading driver, please wait...")
        options = Options()
        options.add_argument("--log-level=3")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://www.google.com")  # Attempt to open a known page
            print(Fore.GREEN + "[+] Driver loaded successfully\n")
        except Exception as e:
            print(Fore.RED + "[!] No internet connection or WebDriver error")
            exit(1)

    def setup_service_xpaths(self): # Define the base URL and xpaths for different services to interact with
        self.url = "https://zefoy.com"
        self.services = {
            "followers": ("/html/body/div[6]/div/div[2]/div/div/div[2]/div/button", 7),
            "hearts": ("/html/body/div[6]/div/div[2]/div/div/div[3]/div/button", 8),
            "comment_hearts": ("/html/body/div[6]/div/div[2]/div/div/div[4]/div/button", 9),
            "views": ("/html/body/div[6]/div/div[2]/div/div/div[5]/div/button", 10),
            "shares": ("/html/body/div[6]/div/div[2]/div/div/div[6]/div/button", 11),
            "favorites": ("/html/body/div[6]/div/div[2]/div/div/div[7]/div/button", 12),
        }

    def check_services(self): # Check each service's availability by attempting to find its web element
        for service, (xpath, div_index) in self.services.items():
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                if element.is_enabled():
                    self.services[service] = (xpath, div_index, Fore.GREEN + "[WORKING]")
                else:
                    self.services[service] = (xpath, div_index, Fore.RED + "[OFFLINE]")
            except NoSuchElementException:
                self.services[service] = (xpath, div_index, Fore.RED + "[OFFLINE]")
        
        # Mark 'comment_hearts' service explicitly as not implemented
        if "comment_hearts" in self.services:
            xpath, div_index = self.services["comment_hearts"][:2]
            self.services["comment_hearts"] = (xpath, div_index, Fore.YELLOW + "[NOT IMPLEMENTED]")


    def start(self): # Main method to start the bot, load the page, and handle user interactions
        self.driver.get(self.url)
        print(Fore.YELLOW + "Please complete the captcha on the website and press Enter here when done...")
        input()
        self.check_services()
        self.choose_service_and_url()
        try:
            while True:
                for video_url in self.video_urls:
                    self.perform_service_action(video_url)
        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Script terminated by user.")
        finally:
            self.driver.quit()


    def choose_service_and_url(self): # Display services to the user for selection and accept video URLs as input
        for index, (service, details) in enumerate(self.services.items(), start=1):
            _, div_index, status = details if len(details) == 3 else (*details, "[STATUS UNKNOWN]")
            print(Fore.BLUE + f"[{index}] {service.ljust(20)} {status}")
        
        choice = int(input(Fore.YELLOW + "[-] Choose an option: "))
        self.service_name = list(self.services.keys())[choice - 1]
        urls_input = input(Fore.MAGENTA + "[-] Enter video URLs separated by a space: ")
        self.video_urls = urls_input.split()
        
        _, self.div_index, _ = self.services[self.service_name]
        self.driver.find_element(By.XPATH, self.services[self.service_name][0]).click()


    def perform_service_action(self, video_url): # Perform the action for the chosen service on the provided video URL
        print(Fore.CYAN + f"[+] Switching URL link to \"{video_url}\"")
        actions = [
            ("clear the URL input", f"/html/body/div[{self.div_index}]/div/form/div/input", "clear"),
            ("enter the video URL", f"/html/body/div[{self.div_index}]/div/form/div/input", "send_keys"),
            ("click the search button", f"/html/body/div[{self.div_index}]/div/form/div/div/button", "click"),
            ("click the send button", f"/html/body/div[{self.div_index}]/div/div/div[1]/div/form/button", "click"),
        ]

        for action_desc, xpath, action_type in actions:
            try:
                element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                if action_type == "clear":
                    element.clear()
                elif action_type == "send_keys":
                    element.send_keys(video_url)
                element.click()
                print(Fore.GREEN + f"[+] Successfully {action_desc}.")
                if action_desc == "click the search button":
                    time.sleep(3)  # Delay after clicking the search button based on load times
            except TimeoutException:
                print(Fore.RED + f"[!] Timeout: Could not {action_desc} within the specified period.")

        # Custom wait time for each service after actions
        min_wait, max_wait = self.service_wait_times[self.service_name]
        wait_time = random.randint(min_wait, max_wait)
        self.countdown_timer(wait_time)

    def countdown_timer(self, duration): # Display a countdown timer for the specified duration
        for i in range(duration, 0, -1):
            print(Fore.CYAN + f"\rWaiting for {i} seconds to proceed...", end="")
            time.sleep(1)
        print()

if __name__ == "__main__":
    bot = Bot()
    bot.start()
