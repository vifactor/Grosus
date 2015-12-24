from app.models import Deputy, Law
from app import db

if __name__=='__main__':
    deputy1 = Deputy(name=u'Володимир Гройсман', group=u'БПП')
    deputy2 = Deputy(name=u'Олег Ляшко', group=u'РП')
    deputy3 = Deputy(name=u'Мустафа Найєм', group=u'БПП')
    
    db.session.add(deputy1)
    db.session.add(deputy2)
    db.session.add(deputy3)
    
    law1 = Law(code = u"3442", title=  
            u"Проект Закону"
             "про внесення змін до Кодексу законів про працю України"
              "(щодо гармонізації законодавства"
               "у сфері запобігання та протидії дискримінації"
               "із правом Європейського Союзу)",
               authors=[deputy1, deputy3])
    
    law2 = Law(code = u"7777в", title=  
            u"Проект закону"
            "про самого радикального з усіх радикальних",
               authors=[deputy2])
    
    db.session.add(law1)
    db.session.add(law2)
    db.session.commit()
