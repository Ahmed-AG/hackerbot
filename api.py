from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import logging

from hackerbot.tools import Splunk, SplunkRequest, SplunkResponse
from hackerbot.logging import (
    logger
)
load_dotenv()


app = FastAPI()



@app.post(
    "/api/tools/splunk",
    summary="Ask a question to Splunk",
)
async def splunk(req: SplunkRequest) -> SplunkResponse:
    try:
        splunk = Splunk()
        answer = splunk.run(req)
    except Exception as e:
        logger.error(f"Error running Splunk tool: {e}")
        raise HTTPException(status_code=500, detail="Error running Splunk tool. Please try again later.")
    return answer
