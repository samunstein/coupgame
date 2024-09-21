from abc import abstractmethod, ABCMeta

from config import PARAM_SPLITTER, COMMAND_END


class CoupMessage:
    @abstractmethod
    def serialize(self) -> str:
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, params: str) -> 'CoupMessage':
        raise NotImplementedError()


class ParseSubclassNameParameters(CoupMessage, metaclass=ABCMeta):
    @classmethod
    def transitive_named_subclasses(cls):
        res = []
        if "message_name" not in cls.__abstractmethods__:
            res.append(cls)
        for sub in cls.__subclasses__():
            res.extend(sub.transitive_named_subclasses())
        return res

    @property
    @abstractmethod
    def message_name(self) -> str:
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, serialized: str) -> 'ParseSubclassNameParameters | None':
        split = serialized.strip(COMMAND_END).split(PARAM_SPLITTER)
        name = split[0]
        for sub in cls.transitive_named_subclasses():
            if sub.message_name == name:
                try:
                    return sub.parse_from_params(split[1:])
                except (IndexError, ValueError):
                    return None

    @classmethod
    @abstractmethod
    def parse_from_params(cls, params: list[str]) -> 'ParseSubclassNameParameters':
        raise NotImplementedError()

    @abstractmethod
    def write_data_str_list(self) -> list[object]:
        raise NotImplementedError()

    def serialize(self) -> str:
        return PARAM_SPLITTER.join([self.message_name] + [str(o) for o in self.write_data_str_list()]) + COMMAND_END
