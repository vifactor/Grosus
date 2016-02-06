#!flask/bin/python3

from app.models import Deputy, Law
from app import db
from selenium import webdriver
import json
import time

# webpage loading time 
delay_time = 1 # second

def get_days(driver):
    """Getting days"""
    driver.get("http://w1.c1.rada.gov.ua/pls/radan_gs09/ns_h1")
    time.sleep(delay_time)

    driver.find_element_by_xpath(".//ul[@class='m_ses']/li[@onclick][3]").click()
    time.sleep(delay_time)

    voting_days = driver.find_elements_by_xpath('//li[@style="background-color:#FFFFAE;"]/a[@href]')
    voting_days = [elem.get_attribute("href") for elem in voting_days]
    return voting_days

def get_laws_from_page(driver, day_link):
    """Loading law page, getting nums and links"""
    driver.get(day_link)
    time.sleep(delay_time)
    laws = driver.find_elements_by_xpath('//div[@class="nomer"]/a')
    law_numbers = [elem.get_attribute("text") for elem in laws if elem.get_attribute("text") != '\xa0']
    law_links = [elem.get_attribute("href") for elem in laws if elem.get_attribute("text") != '\xa0']
    law_name = driver.find_elements_by_xpath('//div[@class="nazva"]')
    law_name = [elem.text for elem in law_name]
    return zip(law_numbers, law_links, law_name)

def get_needed_columns(driver):
    """Getting needed columns"""
    trails = []
    for row in driver.find_elements_by_xpath("//div[@id='Data_gol']/*[@id='list_g']/ul/li")[1:]:
        time.sleep(delay_time)
        #print("   looping through trail rows info")
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
            print("Unsupported format in row: {0}".format(row.text))

    trails_table = []
    for elem in trails:
        if u"Поіменне голосування про проект" in elem[2]:
            trails_table.append(elem)
    needed_columns = [item[0] for item in trails_table]
    #print("\tneeded columns:", needed_columns)
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
        #print("   All columns:", columns)
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

    selected_voting_days = voting_days[15:16]
    nb_voting_days = len(selected_voting_days)
    
    for iday, day_link in enumerate(selected_voting_days):
        laws = get_laws_from_page(driver, day_link)
        nb_laws = len(day_link)
        
        for ilaw, (law_num, law_link, law_name) in enumerate(laws):
            print("Day %d/%d, Law %d/%d" % (iday, nb_voting_days, ilaw, nb_laws))
            print("Processing law number {0}".format(law_num))
            url = law_link + "#ui-tabs-2"
            driver.get(url)
            time.sleep(delay_time + 1)
            try:
                # click 'details'
                driver.find_element_by_xpath(".//div[@class='vid_d']/p[@id='name_input']").click()
                time.sleep(delay_time)

                needed_columns = get_needed_columns(driver)
                dep_list = get_dep_list(driver)
                columns = get_all_column_numbers(driver)
                golosuvannya = get_golosuv_info(driver, needed_columns, columns, dep_list)
                
                ### UNCOMMENT THIS IF YOU WANT TO HAVE ALSO JSON FILES WITH VOTING DATA  
                #with open('data/law_{0}.json'.format(law_num), 'w') as out:
                #    out.write(json.dumps(golosuvannya, indent=2))

                if not Law.query.filter_by(code=law_num).count():
                    print ("\tAdding law: %s - %s" % (law_num, law_name))
                    law = Law(code=law_num, title=law_name, authors=[])
                    db.session.add(law)


                for name in golosuvannya['deputies']:
                     if not Deputy.query.filter_by(name=name).count():
                        print("\tAdding deputy %s" % name)
                        deputy = Deputy(name=name, group="")
                        db.session.add(deputy)
                         
                db.session.commit()
            except Exception as err:
                print("! Smth failed in law {0}, error: {1}".format(law_num, err))
