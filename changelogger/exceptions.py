from typing import TypeVar, Generic, Generator, Optional, Any

# ! Types
AT = TypeVar('AT')
KT = TypeVar('KT')
MessageGeneratorType = Generator[Optional[str], Any, None]

# ! Error Base Class
class MessageError(Exception, Generic[AT, KT]):
    def __init__(self, *args: AT, **kwargs: KT) -> None:
        super().__init__()
        self.args = (' '.join([str(arg) for arg in self.__message__(*args, **kwargs) if arg is not None]), )
        self.__attributes__(*args, **kwargs)
    
    def __attributes__(self, *args: AT, **kwargs: KT) -> None:
        pass
    
    def __message__(self, *args: AT, **kwargs: KT) -> MessageGeneratorType:
        yield

# ! Version Error
class VersionExistError(MessageError):
    def __attributes__(self, version: str, *args, **kwargs):
        self.version = version
    
    def __message__(self, version: str, *args, **kwargs):
        yield f"This version already exists: {repr(version)}."

class VersionNotExistError(MessageError):
    def __attributes__(self, version: str, *args, **kwargs):
        self.version = version
    
    def __message__(self, version: str, *args, **kwargs):
        yield f"Couldn't find such a version: {repr(version)}."

# ! Change Type Error
class ChangeTypeKeyError(MessageError):
    def __attributes__(self, text: str, *args, **kwargs):
        self.text = text
    
    def __message__(self, text: str, *args, **kwargs):
        yield f"There is no type of change under such a key: {repr(text)}."

class ChangeTypeEmojiNotCorrectError(MessageError):
    def __attributes__(self, emoji: str, *args, **kwargs):
        self.emoji = emoji
    
    def __message__(self, emoji: str, *args, **kwargs):
        yield f"Incorrect emoji: {repr(emoji)}."