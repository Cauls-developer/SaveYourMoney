"""Definições de interfaces de repositório para abstrair persistência de dados."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> T:
        ...

    @abstractmethod
    def get(self, entity_id: int) -> Optional[T]:
        ...

    @abstractmethod
    def list(self) -> List[T]:
        ...

    @abstractmethod
    def update(self, entity: T) -> T:
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        ...
