#!/usr/bin/env python
#-*- coding: utf-8 -*-

import collections
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def _build_path(full_path):
    if '?' not in full_path:
        return full_path+'?'

    if 'page' not in full_path:
        return full_path+'&'

    # import pdb;pdb.set_trace();
    str_page = full_path[full_path.find('page'):]
    return full_path.replace(str_page,'')



# def SelfPaginator(request,List,Limit):
#     '''分页模块,用法:
#         1.view中引入：
#         ex:from website.common.CommonPaginator import SelfPaginator

#         2.SelfPaginator需要传入三个参数
#             (1).request:获取请求数据
#             (2).List:为需要分页的数据（一般为*.objects.all()取出来数据）
#             (3).Limit:为每页显示的条数
#         ex:lst = SelfPaginator(request,mList, 5)

#         3.view需要获取SelfPaginator return的lst，并把lst返回给前端模板
#         ex:kwvars = {'lPage':lst,}

#         4.前端需要for循环lPage也就是lst读取每页内容
#         ex:{% for i in lPage %} ... {% endfor %}

#         5.模板页引入paginator.html
#         ex:{% include "common/paginator.html" %}
#     '''

#     paginator = Paginator(List, int(Limit))
#     # import pdb;pdb.set_trace();
#     page = request.GET.get('page')
#     try:
#         lst = paginator.page(page)
#     except PageNotAnInteger:
#         lst = paginator.page(1)
#     except EmptyPage:
#         lst = paginator.page(paginator.num_pages)

#     lst.before_path = _build_path(request.get_full_path())
#     return lst


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


def SelfPaginator(request,count,per_page):
    '''分页模块,用法:
        1.view中引入：
        ex:from website.common.CommonPaginator import SelfPaginator

        2.SelfPaginator需要传入三个参数
            (1).request:获取请求数据
            (2).count:记录数（一般为*.objects.all()取出来数据）
            (3).per_page:为每页显示的条数



        example - django:
            count = Image.objects.all().count()
            page = SelfPaginator(request,count,20)
            mList = Image.objects.all()[page.start_index:page.end_index_django]

            kwvars = {
                'lPage':page,#是否有下一页
                'mList':mList,#界面显示的记录
                'request':request,
            }
            return render_to_response('image/image.list.html',kwvars,RequestContext(request))



        example - raw_sql:
            count = get_kservice_list_count(search)
            page = SelfPaginator(request,count,20)
            mList = get_kservice_list(search,page.start_index,page.end_index)

            kwvars = {
                'lPage':page,#是否有下一页
                'mList':mList,#界面显示的记录
                'request':request,
            }
            return render_to_response('image/image.list.html',kwvars,RequestContext(request))



        3.view需要获取SelfPaginator return的lst，并把lst返回给前端模板
        ex:kwvars = {'mList':mList,}

        4.前端需要for循环mList也就是lst读取每页内容
        ex:{% for i in mList %} ... {% endfor %}

        5.模板页引入paginator.html
        ex:{% include "common/paginator.html" %}
    '''
    paginator = MyPaginator(count,per_page)

    try:
        lst = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        lst = paginator.page(1)
    except EmptyPage:
        lst = paginator.page(paginator.num_pages)

    lst.before_path = _build_path(request.get_full_path())
    # import pdb;pdb.set_trace();
    return lst



class MyPaginator(object):
    def __init__(self,count,per_page):
        '''
        count:数据库所有记录数
        per_page:每页显示多少条记录
        curr_page:当前页数
        '''
        self.count = count
        self.per_page = per_page

        if count == 0: #如果列表为空,则默认只有第一页
            self.num_pages = 1
            return

        if count % per_page ==0:
            self.num_pages=count /per_page #总共的页码
        else:
            self.num_pages=count/per_page+1 #不解释



    def page(self,curr_page):
        return self._get_page(curr_page,self)

    def _get_page(self, *args, **kwargs):
        """
        Returns an instance of a single page.

        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return Page(*args, **kwargs)

class Page(object):
    def __init__(self,curr_page,paginator):
        # '''
        # count:数据库所有记录数
        # per_page:每页显示多少条记录
        # curr_page:当前页数
        # '''
        self.paginator = paginator
        self.curr_page = self.validate_number(curr_page)


    def validate_number(self, number):
        # return number
        """验证页码合法性（是否为正整数）
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.paginator.num_pages:
            if number == 1:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return number

    def has_next(self):
        #判断是否有下一页
        return False if self.curr_page == self.paginator.num_pages else True

    def has_previous(self):
        #判断是否有前一页
        return False if self.curr_page == 1 else True

    def next_page_number(self):
        return self.validate_number(self.curr_page + 1)


    def previous_page_number(self):
        return self.validate_number(self.curr_page - 1)

    @property
    def start_index(self):
        """sql limit start"""
        if self.paginator.count == 0:
            return 0
        return (self.curr_page-1)*self.paginator.per_page

    @property
    def end_index(self):
        """sql limit end"""
        return self.paginator.per_page

    @property
    def end_index_django(self):
        """sql limit end"""
        return self.start_index +self.paginator.per_page
