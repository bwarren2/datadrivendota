from rest_framework_extensions.key_constructor.constructors import (
    DefaultKeyConstructor,
)
from rest_framework_extensions.key_constructor import bits


class ParamKeyConstructor(DefaultKeyConstructor):
    all_query_params = bits.QueryParamsKeyBit()


rest_key_constructor = ParamKeyConstructor()
