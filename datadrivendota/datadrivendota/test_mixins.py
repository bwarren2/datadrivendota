

class UrlTestMixin(object):

    simple_urls = None
    api_urls = None
    prefix = None

    def __init__(self, *args, **kwargs):
        if self.simple_urls is None:
            self.simple_urls = []
        if self.api_urls is None:
            self.api_urls = []
        super(UrlTestMixin, self).__init__(*args, **kwargs)

    def test_simple_urls(self):
        for url in self.simple_urls:
            strng = self.prefix+url
            resp = self.client.get(strng)
            if resp.status_code != 200:
                print strng, resp
            self.assertEqual(resp.status_code, 200)

    def test_api_urls(self):
        for url in self.api_urls:
            strng = self.prefix+url
            resp = self.client.get(
                strng,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            if resp.status_code != 200 or resp.content == 'fail':
                print strng, resp

            self.assertEqual(resp.status_code, 200)
            self.assertNotEqual(resp.content, 'fail')
