from django import template

register = template.Library()


class ActiveNode(template.Node):
    def __init__(self, url_name, main_nav=False):
        self.url_name = url_name
        self.main_nav = main_nav

    def render(self, context):
        request = context.get('request')
        if request is None:
            return ""
        try:
            if self.main_nav and request.resolver_match.namespace:
                full_url_name = '{namespace}'.format(
                    namespace=request.resolver_match.namespace
                )
            elif request.resolver_match.namespace:
                full_url_name = "{namespace}:{url_name}".format(
                    namespace=request.resolver_match.namespace,
                    url_name=request.resolver_match.url_name
                )
            else:
                full_url_name = "{url_name}".format(
                    url_name=request.resolver_match.url_name
                )
            active = full_url_name == self.url_name
            if active:
                return "active"
            else:
                return ""
        except AttributeError:
            return ""


@register.tag
def active(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        token_contents = token.split_contents()
        if len(token_contents) not in (2, 3):
            raise ValueError
        tag_name = token_contents[0]
        url_name = token_contents[1]
        if len(token_contents) == 3:
            main_nav = token_contents[2] == 'main_nav'
        else:
            main_nav = False
    except ValueError:
        raise template.TemplateSyntaxError(
            "{name} tag requires exactly one argument".format(
                name=token.contents.split()[0]
            )
        )
    if not (url_name[0] == url_name[-1] and url_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "{name} tag's argument should be in quotes".format(name=tag_name)
        )
    return ActiveNode(url_name[1:-1], main_nav=main_nav)
