import time
import json
import html
import logging
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException


WEBSITE_URL = "https://kktix.com/"
TARGET_EVENT_NAME = "some_sample_event"
TARGET_EVENT_CATEGORY = "Entertainment"
TARGET_TICKET_PRICES = ["800", "3,200"]
TARGET_TICKET_TYPE = "B1"
TARGET_BUY_PRICE = "800"
TARGET_TICKET_QTY = "2"
PAGE_REFRESH_INTERVAL_SECOND = 1
TICKET_SEARCH_WAITING_TIME_SECOND = 900
WEBSITE_USERNAME = "your_username_here"
WEBSITE_PASSWORD = "your_password_here"
CHROME_DRIVER_PATH = "chromedriver.exe"


logger = logging.getLogger()
fileHandler = logging.FileHandler("logfile.log")
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)

logger.setLevel("INFO")


class TicketBot:
    __slot__ = ['driver']
    def __init__(self, driver):
        self.driver = driver

    def search_event(self):
        logger.info("Searhing event {} ...".format(TARGET_EVENT_NAME))
        category_page = self.driver.find_element(By.LINK_TEXT, TARGET_EVENT_CATEGORY)
        category_page.click()

        search_tex_field = self.driver.find_element(By.ID, "search_form_search")

        search_tex_field.send_keys(TARGET_EVENT_NAME)
        search_tex_field.send_keys(Keys.RETURN)

    def navigate_to_event(self):
        try:
            search_result = self.driver.find_element(
                By.XPATH, '//div[@data-react-class="SearchWrapper"]'
            )
            
            events = json.loads(search_result.get_attribute("data-react-props"))["data"]

            if events is not None:
                for event in events:
                    event_name = html.unescape(event["name"]).strip()
                    logger.info("Found target event {} !".format(event_name))
                    if TARGET_EVENT_NAME == event_name:
                        event_page = self.driver.find_element(
                            By.XPATH, '//a[@href="{}"]'.format(event["public_url"])
                        )
                        event_page.click()

                        next_step = self.driver.find_element(By.LINK_TEXT, "Next Step")
                        next_step.click()

            else:
                logger.error("Event name might be incorrect.")
        except:
            raise Exception("Event not found!")


    def signing_in(self):
        sign_in = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.LINK_TEXT, "Sign In"))
        )
        sign_in.click()

        insert_username = WebDriverWait(self.driver, 1).until(
            ec.presence_of_element_located((By.XPATH, "//input[@id='user_login']"))
        )
        insert_username.send_keys(WEBSITE_USERNAME)

        insert_password = self.driver.find_element(
            By.XPATH, "//input[@id='user_password']"
        )
        insert_password.send_keys(WEBSITE_PASSWORD)

        submit_login = self.driver.find_element(By.XPATH, "//input[@value='Sign In']")
        submit_login.click()

    # def buy_ticket_in_multiple_prices(self):
    #     ticket_table = self.driver.find_element(By.CLASS_NAME ,"display-table")
    #     ticket_list = []
    #     for i in ticket_table:
    #         ticket_list.append(i.get_attribute("id"))

    #     for price in TARGET_TICKET_PRICES:
    #         print("Start buying {}".format(price))
    #         for x in ticket_list:
    #             print("Checking ticket type of {}".format(x))
    #             try:
    #                 ticket_price = self.driver.find_element_by_xpath(
    #                     "//div[@id='{}']//span[contains(@class,'ticket-price')]//span[contains(@class,'ng-binding ng-scope')]".format(
    #                         x
    #                     )
    #                 ).text
    #                 print("Current ticket price {}".format(ticket_price))
    #                 if price in ticket_price:
    #                     ticket_slot = self.driver.find_element_by_xpath(
    #                         "//div[@id='{}']//input[contains(@value,'0')]".format(x)
    #                     )
    #                     ticket_slot.clear()
    #                     ticket_slot.send_keys(TARGET_TICKET_QTY)

    #                     submit_agree = self.driver.find_element_by_xpath(
    #                         "//input[@id='person_agree_terms']"
    #                     )
    #                     submit_agree.click()

    #                     # nextstep2 = driver.find_element_by_xpath("//span[contains(text(),'Next Step')]")
    #                     # nextstep2.click()

    #                     break
    #                 else:
    #                     print("Proceed to next price type")
    #                     continue
    #             except NoSuchElementException as ex:
    #                 print("Sold Out !")

    def buy_single_ticket_price(self):
        is_sale_open = False
        ticket_table = self.driver.find_elements(By.CLASS_NAME, "display-table")
        ticket_types = {}
        for ticket_type_element in ticket_table:
            ticket_type_id = ticket_type_element.get_attribute("id")
            ticket_type_name = self.driver.find_element(
                By.XPATH,
                "//div[@id='{}']//span[@class='ticket-name ng-binding']".format(
                    ticket_type_id
                ),
            ).text
            if "\n" in ticket_type_name:
                ticket_type_name = ticket_type_name.split("\n")[0]
            ticket_types[ticket_type_name] = ticket_type_id

        logger.info(ticket_types)

        while True:
            try:
                if TARGET_TICKET_TYPE in ticket_types:
                    ticket_id = ticket_types[TARGET_TICKET_TYPE]
                    logger.info(
                        "Found a target ticket type {} !".format(TARGET_TICKET_TYPE)
                    )

                    try:
                        self.driver.find_element(
                            By.XPATH,
                            '//*[@id="{}"]/div/span[4]/input'.format(ticket_id),
                        )
                        is_sale_open = True
                        logger.info("Ticket is available for sale.")
                    except:
                        is_sale_open = False
                        logger.info("Ticket is not for sale yet.")
                        self.driver.refresh()
                    if not is_sale_open:
                        sale_status = self.driver.find_element(
                            By.XPATH, '//*[@id="{}"]/div/span[4]'.format(ticket_id)
                        ).text
                        if sale_status == "Not Started":
                            logger.info(
                                "Ticket sale is not open yet. Refresh page to retry."
                            )
                            time.sleep(PAGE_REFRESH_INTERVAL_SECOND)
                            self.driver.refresh()
                            continue
                        elif sale_status == "Sold Out":
                            logger.warning("Sold out")
                            break
                    else:
                        ticket_price = self.driver.find_element(By.XPATH,
                            "//div[@id='{}']//span[contains(@class,'ticket-price')]//span[contains(@class,'ng-binding ng-scope')]".format(
                                ticket_id
                            )
                        ).text

                        if TARGET_BUY_PRICE in ticket_price:
                            logger.info(
                                "Found a target ticket price NTD{} !".format(
                                    TARGET_BUY_PRICE
                                )
                            )
                            ticket_slot = self.driver.find_element(
                                By.XPATH,
                                "//div[@id='{}']//input[contains(@value,'0')]".format(
                                    ticket_id
                                ),
                            )
                            ticket_slot.clear()
                            ticket_slot.send_keys(TARGET_TICKET_QTY)
                            
                            submit_agree = self.driver.find_element(
                                By.XPATH, "//input[@id='person_agree_terms']"
                            )
                            submit_agree.click()
                            
                            confirm_buy = self.driver.find_element(
                                By.XPATH, "//span[contains(text(),'Next Step')]"
                            )
                            confirm_buy.click()
                            
                            # Wait for the ticket searching process
                            self.driver.implicitly_wait(TICKET_SEARCH_WAITING_TIME_SECOND)

                            confirm_ticket = self.driver.find_element(
                                By.XPATH, "//button[contains(text(),'Got it')]"
                            )
                            confirm_ticket.click()

                            self.driver.implicitly_wait(2)
                            
                            confirm_ticket2 = self.driver.find_element(
                                By.LINK_TEXT, "Confirm"
                            )
                            confirm_ticket2.click()

                            confirm_purchase = self.driver.find_element(
                                By.XPATH, "//a[@class='btn btn-primary ng-binding']"
                            )
                            confirm_purchase.click()

                            break
            except NoSuchElementException as ex:
                logger.error(ex)
                continue


def main():
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    driver.get(WEBSITE_URL)

    tb = TicketBot(driver)
    tb.search_event()
    tb.navigate_to_event()
    tb.signing_in()
    driver.implicitly_wait(2)
    tb.buy_single_ticket_price()


if __name__ == "__main__":
    main()
