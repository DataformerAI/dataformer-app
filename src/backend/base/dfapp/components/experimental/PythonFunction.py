from typing import Callable

from dfapp.custom import CustomComponent
from dfapp.custom.utils import get_function
from dfapp.field_typing import Code


class PythonFunctionComponent(CustomComponent):
    display_name = "Python Function"
    description = "Define a Python function."
    icon = "Python"

    def build_config(self):
        return {
            "function_code": {
                "display_name": "Code",
                "info": "The code for the function.",
                "show": True,
            },
        }

    def build(self, function_code: Code) -> Callable:
        self.status = function_code
        func = get_function(function_code)
        return func
