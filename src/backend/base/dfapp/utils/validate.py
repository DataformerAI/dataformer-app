import ast
import contextlib
import importlib
from types import FunctionType
from typing import Dict, List, Optional, Union

from dfapp.field_typing.constants import CUSTOM_COMPONENT_SUPPORTED_TYPES


def add_type_ignores():
    if not hasattr(ast, "TypeIgnore"):

        class TypeIgnore(ast.AST):
            _fields = ()

        ast.TypeIgnore = TypeIgnore


def validate_code(code):
    # Initialize the errors dictionary
    errors = {"imports": {"errors": []}, "function": {"errors": []}}

    # Parse the code string into an abstract syntax tree (AST)
    try:
        tree = ast.parse(code)
    except Exception as e:
        errors["function"]["errors"].append(str(e))
        return errors

    # Add a dummy type_ignores field to the AST
    add_type_ignores()
    tree.type_ignores = []

    # Evaluate the import statements
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                try:
                    importlib.import_module(alias.name)
                except ModuleNotFoundError as e:
                    errors["imports"]["errors"].append(str(e))

    # Evaluate the function definition
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            code_obj = compile(ast.Module(body=[node], type_ignores=[]), "<string>", "exec")
            try:
                exec(code_obj)
            except Exception as e:
                errors["function"]["errors"].append(str(e))

    # Return the errors dictionary
    return errors


def eval_function(function_string: str):
    # Create an empty dictionary to serve as a separate namespace
    namespace: Dict = {}

    # Execute the code string in the new namespace
    exec(function_string, namespace)
    function_object = next(
        (
            obj
            for name, obj in namespace.items()
            if isinstance(obj, FunctionType) and obj.__code__.co_filename == "<string>"
        ),
        None,
    )
    if function_object is None:
        raise ValueError("Function string does not contain a function")
    return function_object


def execute_function(code, function_name, *args, **kwargs):
    add_type_ignores()

    module = ast.parse(code)
    exec_globals = globals().copy()

    for node in module.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                try:
                    exec(
                        f"{alias.asname or alias.name} = importlib.import_module('{alias.name}')",
                        exec_globals,
                        locals(),
                    )
                    exec_globals[alias.asname or alias.name] = importlib.import_module(alias.name)
                except ModuleNotFoundError as e:
                    raise ModuleNotFoundError(f"Module {alias.name} not found. Please install it and try again.") from e

    function_code = next(
        node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    function_code.parent = None
    code_obj = compile(ast.Module(body=[function_code], type_ignores=[]), "<string>", "exec")
    try:
        exec(code_obj, exec_globals, locals())
    except Exception as exc:
        raise ValueError("Function string does not contain a function") from exc

    # Add the function to the exec_globals dictionary
    exec_globals[function_name] = locals()[function_name]

    return exec_globals[function_name](*args, **kwargs)


def create_function(code, function_name):
    if not hasattr(ast, "TypeIgnore"):

        class TypeIgnore(ast.AST):
            _fields = ()

        ast.TypeIgnore = TypeIgnore

    module = ast.parse(code)
    exec_globals = globals().copy()

    for node in module.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                try:
                    exec_globals[alias.asname or alias.name] = importlib.import_module(alias.name)
                except ModuleNotFoundError as e:
                    raise ModuleNotFoundError(f"Module {alias.name} not found. Please install it and try again.") from e

    function_code = next(
        node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    function_code.parent = None
    code_obj = compile(ast.Module(body=[function_code], type_ignores=[]), "<string>", "exec")
    with contextlib.suppress(Exception):
        exec(code_obj, exec_globals, locals())
    exec_globals[function_name] = locals()[function_name]

    # Return a function that imports necessary modules and calls the target function
    def wrapped_function(*args, **kwargs):
        for module_name, module in exec_globals.items():
            if isinstance(module, type(importlib)):
                globals()[module_name] = module

        return exec_globals[function_name](*args, **kwargs)

    return wrapped_function


def create_class(code, class_name):
    """
    Dynamically create a class from a string of code and a specified class name.

    :param code: String containing the Python code defining the class
    :param class_name: Name of the class to be created
    :return: A function that, when called, returns an instance of the created class
    """
    if not hasattr(ast, "TypeIgnore"):
        ast.TypeIgnore = create_type_ignore_class()

    # Replace from dfapp import CustomComponent with from dfapp.custom import CustomComponent
    code = code.replace("from dfapp import CustomComponent", "from dfapp.custom import CustomComponent")
    code = code.replace(
        "from dfapp.custom import CustomComponent",
        "from dfapp.custom import CustomComponent",
    )
    module = ast.parse(code)
    exec_globals = prepare_global_scope(code, module)

    class_code = extract_class_code(module, class_name)
    compiled_class = compile_class_code(class_code)

    return build_class_constructor(compiled_class, exec_globals, class_name)


def create_type_ignore_class():
    """
    Create a TypeIgnore class for AST module if it doesn't exist.

    :return: TypeIgnore class
    """

    class TypeIgnore(ast.AST):
        _fields = ()

    return TypeIgnore


def prepare_global_scope(code, module):
    """
    Prepares the global scope with necessary imports from the provided code module.

    :param module: AST parsed module
    :return: Dictionary representing the global scope with imported modules
    """
    exec_globals = globals().copy()
    exec_globals.update(get_default_imports(code))
    for node in module.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                try:
                    exec_globals[alias.asname or alias.name] = importlib.import_module(alias.name)
                except ModuleNotFoundError as e:
                    raise ModuleNotFoundError(f"Module {alias.name} not found. Please install it and try again.") from e
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            try:
                imported_module = importlib.import_module(node.module)
                for alias in node.names:
                    exec_globals[alias.name] = getattr(imported_module, alias.name)
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f"Module {node.module} not found. Please install it and try again")
    return exec_globals


def extract_class_code(module, class_name):
    """
    Extracts the AST node for the specified class from the module.

    :param module: AST parsed module
    :param class_name: Name of the class to extract
    :return: AST node of the specified class
    """
    class_code = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)

    class_code.parent = None
    return class_code


def compile_class_code(class_code):
    """
    Compiles the AST node of a class into a code object.

    :param class_code: AST node of the class
    :return: Compiled code object of the class
    """
    code_obj = compile(ast.Module(body=[class_code], type_ignores=[]), "<string>", "exec")
    return code_obj


def build_class_constructor(compiled_class, exec_globals, class_name):
    """
    Builds a constructor function for the dynamically created class.

    :param compiled_class: Compiled code object of the class
    :param exec_globals: Global scope with necessary imports
    :param class_name: Name of the class
    :return: Constructor function for the class
    """

    exec(compiled_class, exec_globals, locals())
    exec_globals[class_name] = locals()[class_name]

    # Return a function that imports necessary modules and creates an instance of the target class
    def build_custom_class(*args, **kwargs):
        for module_name, module in exec_globals.items():
            if isinstance(module, type(importlib)):
                globals()[module_name] = module

        instance = exec_globals[class_name](*args, **kwargs)
        return instance

    build_custom_class.__globals__.update(exec_globals)
    return build_custom_class


def get_default_imports(code_string):
    """
    Returns a dictionary of default imports for the dynamic class constructor.
    """

    default_imports = {
        "Optional": Optional,
        "List": List,
        "Dict": Dict,
        "Union": Union,
    }
    dfapp_imports = list(CUSTOM_COMPONENT_SUPPORTED_TYPES.keys())
    necessary_imports = find_names_in_code(code_string, dfapp_imports)
    dfapp_module = importlib.import_module("dfapp.field_typing")
    default_imports.update({name: getattr(dfapp_module, name) for name in necessary_imports})

    return default_imports


def find_names_in_code(code, names):
    """
    Finds if any of the specified names are present in the given code string.

    :param code: The source code as a string.
    :param names: A list of names to check for in the code.
    :return: A set of names that are found in the code.
    """
    found_names = {name for name in names if name in code}
    return found_names


def extract_function_name(code):
    module = ast.parse(code)
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            return node.name
    raise ValueError("No function definition found in the code string")


def extract_class_name(code):
    module = ast.parse(code)
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            return node.name
    raise ValueError("No class definition found in the code string")
