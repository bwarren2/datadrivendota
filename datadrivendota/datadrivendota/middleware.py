class AccessControlAllowOriginMiddleware(object):
    """
    We want non-webkit browsers to properly display CDN-sourced fonts. This
    requires telling them (per spec!) that they can, so we set this header.

    It's actually too permissive, but there's no way to set multiple allowed
    origins that I know of using Django's limited ability to manipulate
    headers. So, ideally, we want to allow just
    https://datadrivendota.s3.amazonaws.com and http://fonts.googleapis.com
    """
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = '*'
        return response
