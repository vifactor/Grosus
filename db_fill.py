#!flask/bin/python3

from app.models import Deputy, Law
from app import db
from selenium import webdriver
import json
import time
# from django.db import IntegrityError

delay_time = 2

def get_days(driver):
    """Getting days"""
    driver.get("http://w1.c1.rada.gov.ua/pls/radan_gs09/ns_h1")
    time.sleep(delay_time)

    driver.find_element_by_xpath(".//ul[@class='m_ses']/li[@onclick][3]").click()
    time.sleep(delay_time + 1)

    voting_days = driver.find_elements_by_xpath('//li[@style="background-color:#FFFFAE;"]/a[@href]')
    voting_days = [elem.get_attribute("href") for elem in voting_days]
    return voting_days

def get_laws_from_page(driver, day_link):
    """Loading law page, getting nums and links"""
    driver.get(day_link)
    time.sleep(delay_time + 1)
    laws = driver.find_elements_by_xpath('//div[@class="nomer"]/a')
    law_numbers = [elem.get_attribute("text") for elem in laws if elem.get_attribute("text") != '\xa0']
    law_links = [elem.get_attribute("href") for elem in laws if elem.get_attribute("text") != '\xa0']
    law_name = driver.find_elements_by_xpath('//div[@class="nazva"]')
    law_name = [elem.text for elem in law_name]
    return zip(law_numbers, law_links, law_name)

def get_needed_columns(driver):
    """Getting needed columns"""
    trails = []
    for row in driver.find_elements_by_xpath("//div[@id='Data_gol']/*[@id='list_g']/ul/li"):
        time.sleep(delay_time + 1)
        print("   looping through trail rows info")
        try:
            row_id = row.find_element_by_xpath(".//div[@class='fr_nomer']").get_attribute("innerHTML")
            row_id = row_id.replace(".", "")
            date = row.find_element_by_xpath(".//div[@class='fr_data']").text  # 'fr_data'
            descr = row.find_element_by_xpath(".//div[@class='fr_nazva']").text
            descr = descr.split("\n")[0]
            votes = row.find_element_by_xpath(".//div[@class='fr_nazva']//center").text
            rishennya = votes.split("-")[-1].split(" ", 1)[1]
            trails.append((row_id, date, descr, rishennya))
        except:
            print("   Error\n Row: \n {0}".format(row.text))

    trails_table = []
    for elem in trails:
        if u"Поіменне голосування про проект" in elem[2]:
            trails_table.append(elem)
    needed_columns = [item[0] for item in trails_table]
    print("\tneeded columns:", needed_columns)
    return needed_columns

def get_dep_list(driver):
    """Getting deputies list"""
    deps = driver.find_elements_by_xpath("//table[@class='tab_gol']/tbody/tr/td[2]") # deputies
    dep_list = [elem.get_attribute("innerHTML") for elem in deps]
    return dep_list

def get_all_column_numbers(driver):
    """Getting all column numbers"""
    headings = driver.find_elements_by_xpath("//*[@id='list_g']/ul/table[1]/tbody/tr[1]")[0].text
    if headings:
        columns = headings.split(" ", 2)[2].split(" ")
        print("   All columns:", columns)
    return columns

def get_golosuv_info(driver, needed_columns, columns, dep_list):
    """Getting voting data"""
    golosuvannya = dict()
    golosuvannya['deputies'] = dep_list
    intesection_needed = set(columns) & set(needed_columns)
    if not bool(intesection_needed):
        print(" ! got no real votings")
    for count in intesection_needed:
        i = int(count) + 2
        votes = driver.find_elements_by_xpath("//table[@class='tab_gol']/tbody//td[%i]"%(i))
        colored_votes = []
        for vote in votes:
            # get element by color
            # 1 = za
            # 2 = proty
            # 3 = utrymavsya
            # 4 = ne golosuvav
            # 5 = vidsutiij
            color = vote.get_attribute("style").replace("color: ", "").replace(";", "").replace("Yellow", "3").replace("green", "1").replace("red", "2")
            if not color:
                if vote.text == '•':
                    color = "4"
                else:
                    color = "5"
            colored_votes.append(color)
        golosuvannya[count] = colored_votes
    return golosuvannya

if __name__ == '__main__':
    driver = webdriver.Firefox()
    voting_days = get_days(driver)
    # import ipdb; ipdb.set_trace()

    for day_link in voting_days[15:16]:
        laws = get_laws_from_page(driver, day_link)
        for law_num, law_link, law_name in laws:
            print("Getting law number {0} page. ".format(law_num))
            url = law_link + "#ui-tabs-2"
            driver.get(url)
            time.sleep(delay_time + 2)
            try:
                # click 'details'
                driver.find_element_by_xpath(".//div[@class='vid_d']/p[@id='name_input']").click()
                time.sleep(delay_time + 1)

                needed_columns = get_needed_columns(driver)
                dep_list = get_dep_list(driver)
                columns = get_all_column_numbers(driver)
                golosuvannya = get_golosuv_info(driver, needed_columns, columns, dep_list)

                with open('data/law_{0}.json'.format(law_num), 'w') as out:
                    out.write(json.dumps(golosuvannya, indent=2))

                if not Law.query.filter_by(code=law_num).count():
                    print ("\tTrying to add a law: %s - %s" % (law_num, law_name))
                    #with db.session.begin_nested():
                    law = Law(code=law_num, title=law_name, authors=[])
                    
                    db.session.add(law)

                    # except IntegrityError:
                    #     law = Law.query.filter(Law.code == law_num).first()

                    # law = Law(code=law_num, title=law_name, authors=[])
                    # db.session.add(law)

                for name in golosuvannya['deputies']:
                     print ("   Checking deputies...")
                     if not Deputy.query.filter_by(name=name).count():
                         deputy = Deputy(name=name, group="")
                         db.session.add(deputy)
                         #print ('Is name a string? - ', isinstance(name, str))
                         print("\tDeputy added: %s" % name)
                         
                db.session.commit()
            except Exception as err:
                print(" ! Smth failed in law {0}, error: {1}".format(law_num, err))
