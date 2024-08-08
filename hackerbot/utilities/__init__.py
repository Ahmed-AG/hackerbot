import os


def env_var_config_default_factory(field_name: str, env_var: str, default: str | None = None, error_on_empty: bool = False) -> str:
    """
        Get the value of an environment variable or return a default value
    """
    value = os.getenv(env_var, default)
    if error_on_empty and value is None:
        raise ValueError(f"{field_name} must be passed as a config argument or as an environmental variable: export {env_var}='value'")
    return value or ""
