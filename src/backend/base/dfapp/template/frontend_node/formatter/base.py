from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel

from dfapp.template.field.base import TemplateField


class FieldFormatter(BaseModel, ABC):
    @abstractmethod
    def format(self, field: TemplateField, name: Optional[str]) -> None:
        pass
