#!/usr/bin/env python

import os

from vweb.htmlpage import HtmlPage
from vweb.html import *
from urllib.parse import urlparse

from header import Header

class NoData(HtmlPage):

    def __init__(self):
        HtmlPage.__init__(self, 'VReports Index')
        self.header = Header(self.title)

        self.style_sheets.extend([
            'css/vreports.css',
            ])

    def getHtmlContent(self):
        '''Return the entire HTML content of the page.
           (Without HTTP Header)
        '''
        return div(self.header.getHeader() + \
                       self.body())
    def body(self):
        href='https://github.com/dlink/vreports/blob/master/README.md'
        readme_link = a('README', href=href)

        href='https://github.com/dlink/vreports'
        source_link = a(href, href=href)


        text = [h1('Welcome to VRreports'),
                'No report config directory specified. You pass report name ' \
                    'in as a parameter like this: "vreports?r=books".',
                'See %s' % readme_link,
                'Source code available: %s' % source_link,
                h2('Here are some Examples'),
                self.examples()]

        style = 'margin: 50px 300px;'

        return div(big('\n'.join(map(p, text))),
                   style=style
                   )

    def examples(self):
        basedir = '/'.join(os.environ['VIRTUAL_ENV'].split('/')[0:-1])
        examples_dir = '%s/examples' % basedir

        examples = []
        for d in os.listdir(examples_dir):
            if not os.path.isdir('%s/%s' % (examples_dir, d)):
                continue
            # check see it is a directory with a main.yaml in it:
            try:
                if 'main.yaml' in  os.listdir('%s/%s' % (examples_dir, d)):
                    link = '/report/%s' % d
                    data = a(d, href=link)
                    examples.append(data)
            except Exception as e:
                continue
            
        return div(p('\n'.join(map(li, examples))))

if __name__ == '__main__':
    NoData().go()
