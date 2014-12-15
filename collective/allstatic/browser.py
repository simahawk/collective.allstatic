#-*- coding: utf-8 -*-

from time import time

from Products.Five.browser import BrowserView

from zope.component import getMultiAdapter

from plone import api
from plone.memoize import ram


def _cachekey(method, self):
    portal_state = getMultiAdapter((self.context, self.request),
                                   name=u'plone_portal_state')
    portal_url = portal_state.portal_url()
    import pdb;pdb.set_trace()
    key = hash((portal_url,
                self.__name__,
                time() // 3600))
    return key


class Base(BrowserView):

    tool_name = None
    _blacklist = []
    _whitelist = []

    def __call__(self, blacklist=None, whitelist=None):
        self.blacklist = blacklist or self._blacklist
        self.whitelist = whitelist or self._whitelist
        return self.get_content()

    def get_content(self):
        ct = self._get_content()
        self._prepare_response()
        return ct

    @ram.cache(_cachekey)
    def _get_content(self):
        res = [
            '/* upd: %s */' % str(time())
        ]
        jstool = api.portal.get_tool(self.tool_name)
        get = jstool.getResourceContent
        if self.whitelist or self.blacklist:
            # we are explictly pulling/dropping resurces
            # so we must include ALL of them and not cached/merged here
            resources = jstool.getResources()
        else:
            resources = jstool.getEvaluatedResources(self.context)

        if self.whitelist:
            resources = [x for x in resources
                         if x.getId() in self.whitelist]
        for resource in resources:
            if resource.getId() in self.blacklist:
                continue
            _content = get(resource.getId(), self.context)
            res.append(_content)
        return ''.join(res)

    def _prepare_response(self):
        pass


class JSView(Base):

    tool_name = 'portal_javascripts'


class CSSView(Base):

    tool_name = 'portal_css'
