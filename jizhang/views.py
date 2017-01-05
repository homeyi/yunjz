#coding=utf-8

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseRedirect,HttpResponse
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv, json

#myApp package
from jizhang.models import Item, Category
from jizhang.forms import ItemForm, CategoryForm, NewCategoryForm, FindItemForm
from jizhang.data_format_func import get_sorted_categories

# shiyan9
# ajax  --done, views.py, new_item.html, jslib
# register auto gen  --done, accounts/views.py,tests.py, jizhang/data_format_func,
# datepicker --done, new_item.html, find_item.html
# find pages --done, views.py, find_item_results.html

PAGE_ITEM_NUM = 5
    
def split_page(request, data, page_item_num):
    side_show_page_num = 2
    
    p = Paginator(data , page_item_num)
    page = request.GET.get('page') # Get page
    try:
        item_page = p.page(page)
    except PageNotAnInteger:
        item_page = p.page(1)
    except EmptyPage:
        item_page = p.page(p.num_pages)     
    
    page_list = [-1]*len(p.page_range)
    
    for i in p.page_range:
        if i==1 or i==p.num_pages or (i<=item_page.number+side_show_page_num and i>=item_page.number-side_show_page_num):
            page_list[i-1]=i
        elif i==item_page.number+side_show_page_num+1 or i==item_page.number-side_show_page_num-1:
            page_list[i-1]=0
    
    return item_page, page_list  


def delete_items(cls,ids):
    for item_id in ids:
        del_item = get_object_or_404(cls, id=item_id)
        del_item.delete()


# Create your views here.
@login_required
def categories(request, template_name='jizhang/categories.html'):
    if request.method == 'POST':
        ## delete categories
        del_ids = request.POST.getlist('del_id')
        delete_items(Category,del_ids)
                
    return render(request, template_name, {"categories":get_sorted_categories(request.user.username)})

@login_required
def show_category(request, pk, template_name='jizhang/items.html'):
    if request.method == 'POST':
        ## delete items
        del_ids = request.POST.getlist('del_id')
        delete_items(Item,del_ids)
            
    item_list = Item.objects.filter(category__user__username=request.user.username).filter(category__id=pk)
    item_page,page_num_list = split_page(request, item_list, PAGE_ITEM_NUM)
    
    return render(request, template_name, {'items':item_page,'page_num_list':page_num_list})

@login_required    
def edit_category(request,pk, template_name='jizhang/new_category.html'):
    out_errors = []
    if request.method == 'POST':
        form = CategoryForm(request,data=request.POST)
        if form.is_valid():
            form.save(pk)
            return HttpResponseRedirect("/jizhang/categories")
    else:
        category_list = get_object_or_404(Category, id=pk) 
        form = CategoryForm(request,instance=category_list)
    return render(request, template_name,{'form':form})

@login_required
def new_category(request, template_name='jizhang/new_category.html'):
    if request.method == 'POST':
        form = NewCategoryForm(request,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/jizhang/categories")
    else:
        form = NewCategoryForm(request)
    return render(request, template_name, {'form':form})


@login_required
def items(request, template_name='jizhang/items.html'):
    if request.method == 'POST':
        ## delete items
        del_ids = request.POST.getlist('del_id')
        delete_items(Item,del_ids)

    item_list = Item.objects.filter(category__user__username=request.user.username)
    item_page,page_num_list = split_page(request, item_list, PAGE_ITEM_NUM)

    return render(request, template_name, {'items':item_page,'page_num_list':page_num_list})


@login_required 
def edit_item(request, pk, template_name='jizhang/new_item.html'):
    if request.method == 'POST':

        form = ItemForm(request,data=request.POST)
        if form.is_valid():
            form.save(pk)
            return HttpResponseRedirect("/jizhang")
    else:
        item_list = get_object_or_404(Item, id=pk)
        form = ItemForm(request,instance=item_list)

    return render(request, template_name,{'form':form})


@login_required 
def new_item(request, template_name='jizhang/new_item.html'):
    if request.method == 'POST':
        form = ItemForm(request,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/jizhang")
    else:
        form = ItemForm(request,initial={'pub_date':timezone.now().date()})

    return render(request, template_name,{'form':form})


def config_qset(query):
    qset = (
            Q(comment__icontains=query)
        )
    return qset

def config_category_qset(id):
    qset = ()
    ff = get_object_or_404(Category, id=id)
    qset = (Q(category__id=ff.id))
    
    for child in ff.childs.all():
        qset = qset | config_category_qset(child.id)

    return qset
    
@login_required 
def find_item(request):
    if request.method == 'POST':
        del_ids = request.POST.getlist('del_id')
        
        if del_ids:
            for item_id in del_ids:
                del_item = get_object_or_404(Item, id=item_id)
                del_item.delete()
            return HttpResponseRedirect("/jizhang")
                
        else:    

            form = FindItemForm(request,data=request.POST)
            if form.is_valid():
                # time search
                if not form.cleaned_data['start_date']:
                    item_list = Item.objects.filter(category__user__username=request.user.username).all()
                else:
                    item_list = Item.objects.filter(category__user__username=request.user.username).filter(pub_date__range=(form.cleaned_data['start_date'],form.cleaned_data['end_date']))

                # category search
                category_id = form.cleaned_data['category']
                if not category_id:
                    item_category = item_list
                else:
                    category_qset=config_category_qset(category_id)
                    item_category = item_list.filter(category_qset).distinct()

                # key words search
                query = form.cleaned_data['query']
                if not query:   
                    results = item_category
                else:                
                    query_list = query.strip().split(' ')
                    qset =()
                    for every_query in query_list:
                        if not qset:
                            qset = config_qset(every_query)
                        else:
                            qset = qset|config_qset(every_query)

                    results = item_category.filter(qset).distinct()
                    
                p = Paginator(results , PAGE_ITEM_NUM)
                item_pages = []
                for i in p.page_range:
                    item_pages.append(p.page(i))
                    
                return render(request,'jizhang/find_item_results.html', {'item_pages': item_pages})
    else:
        form = FindItemForm(request,initial={'start_date':None,'end_date':timezone.now().date()})
    return render(request,'jizhang/find_item.html',{'form':form})
    
    

@login_required    
def autocomplete_comments(request):
    term = request.GET.get('term')

    if not term:
        items=Item.objects.filter(category__user__username=request.user.username)[:12]
    else:
        items=Item.objects.filter(category__user__username=request.user.username).filter(comment__icontains=term)[:12]
    
    print (items)
    json_send = []
    have_track = []
    for item in items:
        if [item.comment,item.category.id] not in have_track:
            have_track.append([item.comment,item.category.id])
            json_send.append({"id": item.id,
                             "category_id": item.category.id,
                             "label": item.comment+"--"+item.category.name,
                             "value": item.comment
                             })
                             
    print (have_track,json_send)
    return HttpResponse(json.dumps(json_send), content_type="application/json") 
