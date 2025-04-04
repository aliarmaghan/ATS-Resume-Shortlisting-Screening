# langchain_utils.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(model_name="gpt-3.5-turbo")

def score_resume_against_role(resume_text, job_description):
    prompt = PromptTemplate(
        input_variables=["resume", "jd"],
        template="Compare the resume: {resume} with the job description: {jd}. Give a score out of 10 and justify."
    )
    return llm(prompt.format(resume=resume_text, jd=job_description)).content
