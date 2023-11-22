from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import glob
import time


browser = Selenium()

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    login()
    get_orders()
    Archive_file()


def open_robot_order_website():
    browser.open_available_browser("https://robotsparebinindustries.com/#/robot-order")
    
    
#def open_robot_order_website():
#    browser.goto("https://robotsparebinindustries.com/#/robot-order")
 
def login():
    browser.click_button('//*[@id="root"]/div/div[2]/div/div/div/div/div/button[1]')
    
    #page = browser.page()
    #page.click('button:text("OK")')
    

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    browser.maximize_browser_window()


    library = Tables()
    orders = library.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])

    for customer in orders:
  
        browser.select_from_list_by_value(f'//*[@id="head"]',customer['Head'])
        browser.find_element(f'//*[@id="id-body-{customer["Body"]}"]').click()
        browser.find_elements('//*[@class="form-control"]')[0].clear()
        browser.find_elements('//*[@class="form-control"]')[0].send_keys(customer["Legs"])
        browser.find_element('//*[@id="address"]').clear()
        browser.find_element('//*[@id="address"]').send_keys(customer['Address'])
        browser.click_element_when_clickable('//*[@id="order"]')
        for i in range(10):
            time.sleep(1)
            if browser.is_element_visible('//*[@id="order-another"]'):
                break
            else:
                browser.click_element_when_clickable('//*[@id="order"]')


        img_capture = browser.find_element('//*[@id="root"]/div/div[1]/div/div[2]')
        img_capture.screenshot('Output//screenshot.png')
        filename = browser.get_text('//*[@id="receipt"]/p[1]')
        pdf = PDF()
        text = browser.get_text('//*[@id="receipt"]')
        pdf.html_to_pdf(text, f"output//{filename}.pdf")
        #pdf.open_pdf(f"output//{filename}.pdf")
        pdf.add_watermark_image_to_pdf(
            image_path="output//screenshot.png",
            source_path=f"output//{filename}.pdf",
            output_path=f"output//{filename}.pdf"
        )


        browser.click_element_when_clickable('//*[@id="order-another"]')
        login()
        
def Archive_file():
    files = glob.glob(r'output\*.pdf')
    print(files)
    lib = Archive()
    #lib.archive_folder_with_zip(archive_name = 'robottask.zip', members=files)
    lib.archive_folder_with_zip('./output', './output/robottasks.zip', include='*.pdf')



