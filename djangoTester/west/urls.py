# -*- coding: utf-8 -*-
'''
Created on 2015年5月25日

@author: Edward
'''

from django.conf.urls import patterns,url,include
from django.conf.urls.i18n import urlpatterns

urlpatterns = patterns('',
                       url(r'^$','west.views.first_page'),
                       url(r'^staff','west.views.staff'),
                       url(r'^templay','west.views.templay'),
                       url(r'^bootstrap3','west.views.bootstrap3')
                       )
