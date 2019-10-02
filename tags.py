from django.template.library import InclusionNode, parse_bits
from inspect import getfullargspec
import functools


def block_inclusion_tag(func=None, name=None, tag_name='custom_tag', context_text_name='custom_text'):
    takes_context = True
    template_name = ''
    end_tag_name = 'end_{}'.format(tag_name)

    class CustomNode(InclusionNode):
        def render(self, context):
            context[context_text_name] = self.kwargs[context_text_name].render(context)
            self.kwargs.pop(context_text_name)
            return super(CustomNode, self).render(context)

    def dec(func):
        params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(func)
        function_name = (name or getattr(func, '_decorated_function', func).__name__)

        @functools.wraps(func)
        def compile_func(parser, token):
            bits = token.split_contents()[1:]
            args, kwargs = parse_bits(
                parser, bits, params, varargs, varkw, defaults,
                kwonly, kwonly_defaults, takes_context, function_name,
            )

            kwargs[context_text_name] = parser.parse((end_tag_name, tag_name))
            parser.delete_first_token()

            return CustomNode(func, takes_context, args, kwargs, filename,)
        register.tag(function_name, compile_func)
        return func
    return dec

@block_inclusion_tag(tag_name='my_custom_tag', context_text_name='context_text')
def my_custom_tag(context, any_variable=''):
    context['any_variable'] = any_variable
    return context


usage = '''
Usage example:
<div>
{% my_custom_tag any_variable='stringasdasd'%}
  <h1>hello world</h1>
{% end_my_custom_tag %}
</div>
'''

tempalte = '''
Template
<p width="50">
    {{ context_text }}</br>
    <span>{{ any_variable }}</span>
</p>
'''

result = '''
Result :
------------------------
<div>
    <p width="50">
        <h1>hello world</h1></br>stringasdasd
    </p>
</div>
'''
