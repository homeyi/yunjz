#coding=utf-8

from jizhang.models import Category

def sort_categories(categories,list):
    for category in categories:
        list.append(category)
        sort_categories(category.childs.all(),list)
	
def get_sorted_categories(username):
    categories=[]
    category_list = Category.objects.filter(user__username=username).filter(p_category=None).all()
    sort_categories(category_list,categories)
    return categories


# use after register
def auto_gen_categories(userid):
    new_category=Category(name=u'工作收入',isIncome=True,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'工资收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'股票收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'奖金收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'其他收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    
    new_category=Category(name=u'餐饮',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'早餐',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'午餐',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'晚餐',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'饮料水果',isIncome=False,user_id=userid,p_category_id=pid)    
    sub_category.save()
    sub_category=Category(name=u'零食',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save()
    
    new_category=Category(name=u'交通',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'公交地铁',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'加油',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'停车过路',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'汽车保养',isIncome=False,user_id=userid,p_category_id=pid)    
    sub_category.save()
    sub_category=Category(name=u'打的',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save()
    
    new_category=Category(name=u'购物',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'生活用品',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'衣裤鞋帽',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'化妆品',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'首饰手表',isIncome=False,user_id=userid,p_category_id=pid)    
    sub_category.save()
    sub_category=Category(name=u'宝宝用品',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save()    
    sub_category=Category(name=u'书籍报刊',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save() 
    
    new_category=Category(name=u'医疗',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'看病门诊',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'药店买药',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'保健品',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
