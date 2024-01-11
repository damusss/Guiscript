
class UIError(Exception):
    """Base error class for guiscript errors"""
    ...


class UIScriptError(UIError):
    """Error class for errors related to script execution"""
    ...
