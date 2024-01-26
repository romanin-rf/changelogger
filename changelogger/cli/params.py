import re
import validators
from click import ParamType
from click.core import Context, Parameter
from typing import Optional, Any
from .units import VERSION_PATTERN

# ! Regex Param Type Class
class RegexMatch(ParamType):
    name = 'regexable'
    
    def __init__(
        self,
        regex: str=r'',
        flags: int=0
    ) -> None:
        self.regex = regex
        self.flags = flags
    
    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]) -> str:
        try:
            if re.match(self.regex, str(value), self.flags) is not None:
                return str(value)
        except Exception as e:
            self.fail(' '.join([str(arg) for arg in e.args]), param, ctx)
        self.fail("The value does not match the regex expression.", param, ctx)

# ! Version Param Type Class
class Version(RegexMatch):
    name = 'version'
    
    def __init__(self) -> None:
        super().__init__(VERSION_PATTERN)

# ! URL Param Type Class
class URL(ParamType):
    name = 'url'
    
    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]) -> str:
        if validators.url(str(value)):
            return str(value)
        self.fail("This value is not a link.", param, ctx)

# ! Emoji Param Type Class
class Emoji(ParamType):
    name = 'emoji'
    
    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]) -> str:
        value = str(value)
        if len(value) == 1:
            if 169 >= ord(value) <= 128709:
                return str(value)
        self.fail("Value is incorrect", param, ctx)

# ! Union Param Type Class
class Union(ParamType):
    name = 'union'
    
    def __init__(self, *types: type) -> None:
        self.types = types
    
    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]) -> Any:
        for tp in self.types:
            try:
                return tp(value)
            except:
                pass
        self.fail(f"This value is not type: {' | '.join([tp.__class__.__name__ for tp in self.types])}", param, ctx)