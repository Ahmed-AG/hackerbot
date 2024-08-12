from typing import Type, Tuple
import tomlkit
from pathlib import Path
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)


from hackerbot.tools.splunk import SplunkToolConfig


DEFAULT_CONFIG_PATH = f"{Path.home()}/.hackerbot/config.toml"


class HackerbotConfig(BaseSettings):
    _instance = None
    _is_initialized = False

    model_config: SettingsConfigDict = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="hackerbot_",
        # The order of the sources is important. This is sorted from lowest to highest priority
        toml_file=[DEFAULT_CONFIG_PATH, ".hackerbot.toml"],
    )

    splunk: SplunkToolConfig = Field(
        default=SplunkToolConfig(),
        description="Splunk Configuration",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, env_settings, dotenv_settings, TomlConfigSettingsSource(settings_cls),)

    def save_config(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(tomlkit.dumps(self.model_dump()))

    def save_config_default(self) -> None:
        """
            Save the configuration to the default path -> ~/.hackerbot/config.toml
        """
        self.save_config(DEFAULT_CONFIG_PATH)
