from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException

website = "https://kktix.com/"
selected_event = "eventName"
price_list = ["800", "1,800"]
buy_price = "1,800"
num_ticket = "2"
username = #username
pwd = #password


def navigate_to_event():
    events = driver.find_elements_by_tag_name("h2")
    event_list = []
    for event in events:
        event_list.append(event.get_attribute("data-reactid"))

    for y in event_list:
        try:
            event_name = driver.find_element_by_xpath("//h2[contains(@data-reactid,'{}')]".format(y))
            event_name_text = event_name.text
            if selected_event in event_name_text:
                event_name.click()

                nextstep = driver.find_element_by_link_text("Next Step")
                nextstep.click()

        except NoSuchElementException as ex:
            print(ex)


def signing_in():
    sign_in = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.LINK_TEXT, "Sign In")))
    # driver.find_element_by_xpath("//a[@class='btn btn-primary pull-left ng-binding'][contains(text(),'Sign In')]")
    sign_in.click()

    insert_username = WebDriverWait(driver, 1).until(
        ec.presence_of_element_located((By.XPATH, "//input[@id='user_login']")))
    # driver.find_element_by_xpath("//input[@id='user_login']")
    insert_username.send_keys(username)

    insert_password = driver.find_element_by_xpath("//input[@id='user_password']")
    insert_password.send_keys(pwd)

    submit_login = driver.find_element_by_xpath("//input[@value='Sign In']")
    submit_login.click()


def buy_ticket():
    ticket_table = driver.find_elements_by_class_name("display-table")
    ticket_list = []
    for i in ticket_table:
        ticket_list.append(i.get_attribute("id"))

    for price in price_list:
        print("Start buying {}".format(price))
        for x in ticket_list:
            print("Checking ticket type of {}".format(x))
            try:
                ticket_price = driver.find_element_by_xpath(
                    "//div[@id='{}']//span[contains(@class,'ticket-price')]//span[contains(@class,'ng-binding ng-scope')]".format(
                        x)).text
                print("Current ticket price {}".format(ticket_price))
                if price in ticket_price:
                    ticket_slot = driver.find_element_by_xpath("//div[@id='{}']//input[contains(@value,'0')]".format(x))
                    ticket_slot.clear()
                    ticket_slot.send_keys(num_ticket)

                    submit_agree = driver.find_element_by_xpath("//input[@id='person_agree_terms']")
                    submit_agree.click()

                    # nextstep2 = driver.find_element_by_xpath("//span[contains(text(),'Next Step')]")
                    # nextstep2.click()

                    break
                else:
                    print("Proceed to next price type")
                    continue
            except NoSuchElementException as ex:
                print("Sold Out !")


def buy_ticket2():
    ticket_table = driver.find_elements_by_class_name("display-table")
    ticket_list = []
    for i in ticket_table:
        ticket_list.append(i.get_attribute("id"))

    while True:
        for ticket_id in ticket_list:
            try:
                ticket_type = driver.find_element_by_xpath("//div[@id='{}']//span[@class='ticket-name ng-binding']".format(ticket_id)).text
                if "全票" in ticket_type:
                    ticket_price = driver.find_element_by_xpath(
                        "//div[@id='{}']//span[contains(@class,'ticket-price')]//span[contains(@class,'ng-binding ng-scope')]".format(
                            ticket_id)).text
                    if buy_price in ticket_price:
                        ticket_slot = driver.find_element_by_xpath(
                            "//div[@id='{}']//input[contains(@value,'0')]".format(ticket_id))
                        ticket_slot.clear()
                        ticket_slot.send_keys(num_ticket)

                        submit_agree = driver.find_element_by_xpath("//input[@id='person_agree_terms']")
                        submit_agree.click()

                        confirm_buy = driver.find_element_by_xpath("//span[contains(text(),'Next Step')]")
                        confirm_buy.click()

                        confirm_ticket = driver.find_element_by_xpath("//button[contains(text(),'Got it')]")
                        confirm_ticket.click()

                        driver.implicitly_wait(2)

                        #confirm_ticket2 = driver.find_element_by_xpath("//div[@class='btn-group-for-seat']//button[@type='button']")
                        #confirm_ticket2.click()

                        confirm_ticket2 = driver.find_element_by_link_text("Confirm")
                        confirm_ticket2.click()

                        confirm_purchase = driver.find_element_by_xpath("//a[@class='btn btn-primary ng-binding']")
                        confirm_purchase.click()

                        break
            except NoSuchElementException as ex:
                #print("Sold Out!")
                print(ex)
                continue


chromedriver = "/DATA/chromedriver/chromedriver"
driver = webdriver.Chrome(chromedriver)
driver.get(website)


navigate_to_event()
signing_in()
driver.implicitly_wait(2)
buy_ticket2()
