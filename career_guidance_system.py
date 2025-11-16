from langchain_openai import ChatOpenAI
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain_community.utilities import SerpAPIWrapper
from datetime import datetime
import os
import time

class CareerGuidanceSystem:
    def __init__(self, openai_api_key=None, serpapi_key=None):
        """Initialise the career guidance system."""
        self.openai_api_key = openai_api_key
        self.serpapi_key = serpapi_key

        if openai_api_key:
          os.environ["OPENAI_API_KEY"] = openai_api_key

        if serpapi_key:
          os.environ["SERPAPI_API_KEY"] = serpapi_key 

