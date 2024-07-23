from ollama import Client
import logging

logger = logging.getLogger("hackerbot")


class BaseTool:
    _supported_models: list[str] = ["llama3"]
    _llm_model: str = "llama3"
    _llm_url: str | None = None
    _llm_client: Client | None = None

    def _get_llm_client(self) -> Client:
        """
            Get the LLM client
        """
        assert self._llm_url is not None, "LLM URL is not set"

        if self._llm_client is None:
            self._llm_client = Client(host=self._llm_url)
        return self._llm_client

    def _log_model_metrics(self, response: dict) -> None:
        logger.debug("Logging model metrics")

        if hasattr(self, f"_log_{self._llm_model}_metrics") is False:
            logger.warning(f"No metrics logging for model {self._llm_model} defined")
            return
        else:
            getattr(self, f"_log_{self._llm_model}_metrics")(response)

    def _log_llama3_metrics(self, response: dict) -> None:
        total_duration = response.get('total_duration')
        if total_duration is not None:
            total_duration = response.get('total_duration') / 1_000_000_000
        else:
            total_duration = 'N/A'

        load_duration = response.get('load_duration')
        if load_duration is not None:
            load_duration = response.get('load_duration') / 1_000_000_000
        else:
            load_duration = 'N/A'

        logger.info(f"Total Duration: {total_duration} seconds")
        logger.info(f"Load Duration: {load_duration} seconds")
