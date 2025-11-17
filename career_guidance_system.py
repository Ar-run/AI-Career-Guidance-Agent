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

      if openai_api_key:
         self.llm=ChatOpenAI(
            temperature=0.2,
            model="gpt-3.5-turbo-16k",
            openai_api_key=openai_api_key
         )
      else:
         self.llm=None
         self.search=None
         self.search_agent=None

      if serpapi_key:
         self.search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
         self.tools = load_tools(["serpapi"], llm=self.llm)
         self.search_agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=6
         )
      else:
         self.search=None
         self.search_agent

      self.career_data={}
      self.search_cache={}
      self.user_profile={}

      self.fallback_career_options= {
         "Technology": [
            "Software Engineering",
            "Data Science",
            "Cybersecurity",
            "AI/ML Engineering",
            "DevOps",
            "Cloud Architecture",
            "Mobile Development"
         ],
         "Healthcare": [
            "Medicine",
            "Nursing",
            "Pharmacy",
            "Biomedical Engineering",
            "Healthcare Administration",
            "Physical Therapy"
         ],
         "Business": [
            "Finance",
            "Marketing",
            "Management",
            "Human Resources",
            "Entrepreneurship",
            "Business Analysis"
         ],
         "Creative": [
            "Graphic Design",
            "UI/UX Design",
            "Content Creation",
            "Digital Marketing",
            "Animation",
            "Film Production"
         ]
      }
   
   def search_with_cache(self, query, cache_key, ttl_hours=24, max_retries=3):
      """Perform a search with caching and retry mechanism."""

      if cache_key in self.search_cache:
         timestamp = self.search_cache[cache_key]['timestamp']
         age_hours = (datetime.now() - timestamp).total_seconds() / 3600
         if age_hours < ttl_hours:
            return self.search_cache[cache_key]['data']
         
      if self.search_agent:
         retry_count = 0
         last_error = None
         while retry_count < max_retries:
            try:
               result = self.search_agent.run(query)
               #Cache the result with timestamp
               self.search_cache[cache_key] = {
                  'data': result,
                  'timestamp': datetime.now()
               }
               time.sleep(1)  # brief pause to respect rate limits
               return result
            except Exception as e:
               last_error = str(e)
               retry_count += 1
               time.sleep(2)

         try:
            prompt=PromptTemplate(
               input_variables=["query"],
               template="""
               Please provide information on the following: {query} 
               Structure your response clearly with heading and bullet points.
               """
            )
            chain=LLMChain(llm=self.llm, prompt=prompt)
            result=chain.run(query=query)
            #Cache the result with timestamp
            self.search_cache[cache_key] = {
               'data': result,
               'timestamp': datetime.now()
            }
            return result
         
         except:
            return f"Search failed after {max_retries} attempts. Last error: {last_error}"
         
      else:
         return "Search unavailable. Please provide a SerpAPI key for web search capabilities."
      
   def format_search_results(self,results,title):
      """Format search results into a well-structured markdown format"""
      formatted = f"# {title}\n\n"

      #Clean up and format the results

      if isinstance(results,str):
         #Remove and warnings or errors from the output
         lines=results.split('\n')
         clean_lines=[]
         for line in lines:
            if "I'll search for" not in line and "I need to search for" not in line:
               if not line.startswith("Action:") and not line.startswith("Observation:"):
                  clean_lines.append(line)
         
         formatted += "\n".join(clean_lines)
      
      else:
         formatted += "No results available."

      return formatted
   
   def get_career_options(self):
      """Return all available career categrories and options"""

      return self.fallback_career_options




         
         
        


