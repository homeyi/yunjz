#coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget

# Register your models here.
from jizhang.models import Item, Category
from jizhang.data_format_func import get_sorted_categories
		
class CategoryForm(ModelForm):

    class Meta:
        model = Category
        fields = ('name', 'p_category', 'isIncome')


    def __init__(self, request, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.user = request.user
        
        categories=get_sorted_categories(self.user.username)
        
        self.fields['p_category'].widget = forms.Select(attrs={'class':"form-control"})
        self.fields['p_category'].choices = [('',u'----------------')] + [(c.id,c) for c in categories]

        self.fields['name'].widget = forms.TextInput(attrs={'class':"form-control"})
        self.fields['isIncome'].widget = forms.CheckboxInput(attrs={'checkbox':True})

    def clean_isIncome(self):
        if self.cleaned_data['p_category']:
            if not self.cleaned_data['p_category'].isIncome==self.cleaned_data['isIncome']:
                raise forms.ValidationError(u"是否收入应和父类别一致.")	
        return self.cleaned_data['isIncome']

    def save(self,id=None):
        new_category = Category(name=self.cleaned_data['name'],
        p_category=self.cleaned_data['p_category'],
        user = self.user,
        isIncome=self.cleaned_data['isIncome'],
        id = id)
        new_category.save()

class NewCategoryForm(CategoryForm):

	# new category name must not repeat
    def clean_name(self):
        try:
            # user = request.user
            repeat_category = Category.objects.filter(user__username=self.user.username).get(name=self.cleaned_data['name'])
        except Category.DoesNotExist:
            return self.cleaned_data['name']
        raise forms.ValidationError(u"该名称类别已有，请使用其他的名称.")	


class ItemForm(ModelForm):

    class Meta:
        model = Item
        fields = ('pub_date', 'category', 'price', 'comment')

    def save(self, id=None):
        new_item = Item(category=self.cleaned_data['category'],
            price=self.cleaned_data['price'],
            pub_date=self.cleaned_data['pub_date'],
            comment=self.cleaned_data['comment'],
            id = id)            
        new_item.save()
        
    def __init__(self, request, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        
        categories=get_sorted_categories(request.user.username)
        
        self.fields['category'].widget = forms.Select(attrs={'class':"form-control"})
        self.fields['category'].choices = [(c.id,c) for c in categories]
        
        self.fields['pub_date'].widget = forms.DateInput(attrs={'class':"datepicker form-control"})
        self.fields['price'].widget = forms.TextInput(attrs={'class':"form-control"})
        self.fields['comment'].widget = forms.TextInput(attrs={'class':"form-control"})


class FindItemForm(forms.Form):	
	start_date = forms.DateField(label=u'开始时间',required=False, widget=forms.DateInput(attrs={'size': 20,'class':"datepicker form-control"}))
	end_date = forms.DateField(label=u'结束时间',widget=forms.DateInput(attrs={'size': 20,'class':"datepicker form-control"}))
	category = forms.ChoiceField(label=u'选择分类',required=False)
	query = forms.CharField(label=u'备注关键字',required=False,widget=forms.TextInput(attrs={'class':"form-control"}))	
	
	def __init__(self, request, *args, **kwargs):
		super(FindItemForm, self).__init__(*args, **kwargs)
		categories=get_sorted_categories(request.user.username)
					
		self.fields['category'].widget = forms.Select(attrs={'class':"form-control"})
		self.fields['category'].choices = [('',u'所有分类')] + [(c.id,c) for c in categories]	

	def clean_query(self):
		if not self.cleaned_data['start_date']:
			if not self.cleaned_data['query']:
				raise forms.ValidationError(u"开始时间和关键字至少要有一个.")
		return self.cleaned_data['query']
        
	def clean_end_date(self):
		if not self.cleaned_data['start_date']:
			return self.cleaned_data['end_date']
		else:
			if self.cleaned_data['end_date'] > self.cleaned_data['start_date']:
				return self.cleaned_data['end_date']
			else:
				raise forms.ValidationError(u"结束时间需要晚于开始时间.")	