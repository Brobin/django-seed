from inspect import getargspec
from django import template
from django.template.base import TagHelperNode, TemplateSyntaxError, parse_bits

register = template.Library()

from django_faker import Faker

def optional_assignment_tag(func=None, takes_context=None, name=None):
    """
    https://groups.google.com/forum/?fromgroups=#!topic/django-developers/E0XWFrkRMGc
    new template tags type
    """
    def dec(func):
        params, varargs, varkw, defaults = getargspec(func)

        class AssignmentNode(TagHelperNode):
            def __init__(self, takes_context, args, kwargs, target_var=None):
                super(AssignmentNode, self).__init__(takes_context, args, kwargs)
                self.target_var = target_var

            def render(self, context):
                resolved_args, resolved_kwargs = self.get_resolved_arguments(context)
                output = func(*resolved_args, **resolved_kwargs)
                if self.target_var is None:
                    return output
                else:
                    context[self.target_var] = output
                return ''

        function_name = (name or
                         getattr(func, '_decorated_function', func).__name__)

        def compile_func(parser, token):
            bits = token.split_contents()[1:]
            if len(bits) < 2 or bits[-2] != 'as':
                target_var = None
            else:
                target_var = bits[-1]
                bits = bits[:-2]
            args, kwargs = parse_bits(parser, bits, params,
                varargs, varkw, defaults, takes_context, function_name)
            return AssignmentNode(takes_context, args, kwargs, target_var)

        compile_func.__doc__ = func.__doc__
        register.tag(function_name, compile_func)
        return func
    if func is None:
        # @register.assignment_tag(...)
        return dec
    elif callable(func):
        # @register.assignment_tag
        return dec(func)
    else:
        raise TemplateSyntaxError("Invalid arguments provided to assignment_tag")

@optional_assignment_tag(name='fake')
def do_fake( formatter, *args, **kwargs ):
    """
        call a faker format
        uses:

            {% fake "formatterName" *args **kwargs as myvar %}
            {{ myvar }}

        or:
            {% fake 'name' %}

        """
    return Faker.getGenerator().format( formatter, *args, **kwargs )


#@register.assignment_tag(name='fake')
#def fake_tag_as( formatter, *args, **kwargs ):
#    """
#    call a faker format
#    uses:
#
#        {% fake "formatterName" *args **kwargs as myvar %}
#
#    """
#    return Faker.getGenerator().format( formatter, *args, **kwargs )

#@register.simple_tag(name='fakestr')
#def fake_tag_str( formatter, *args, **kwargs ):
#    """
#    call a faker format
#    uses:
#
#        {% fakestr "formatterName" *values **kwargs %}
#    """
#    if formatter == 'dateTimeThisCentury' : print args, kwargs
#    return Faker.getGenerator().format( formatter, *args, **kwargs )

@register.filter(name='fake')
def do_fake_filter( formatter, arg=None ):
    """
    call a faker format
    uses:

        {{ 'randomElement'|fake:mylist }}
        {% if 'boolean'|fake:30 %} .. {% endif %}
        {% for word in 'words'|fake:times %}{{ word }}\n{% endfor %}

    """
    args = []
    if not arg is None: args.append(arg)
    return Faker.getGenerator().format( formatter, *args )


@register.filter(name='or_fake')
def do_or_fake_filter( value, formatter ):
    """
    call a faker if value is None
    uses:

        {{ myint|or_fake:'randomInt' }}

    """
    if not value:
        value = Faker.getGenerator().format( formatter )
    return value


@register.filter
def get_range( value ):
    """
        http://djangosnippets.org/snippets/1357/

      Filter - returns a list containing range made from given value
      Usage (in template):

      <ul>{% for i in 3|get_range %}
        <li>{{ i }}. Do something</li>
      {% endfor %}</ul>

      Results with the HTML:
      <ul>
        <li>0. Do something</li>
        <li>1. Do something</li>
        <li>2. Do something</li>
      </ul>

      Instead of 3 one may use the variable set in the views
    """
    return range( value )