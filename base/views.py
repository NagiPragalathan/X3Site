# chatapp/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import json
import markdown
from langchain.llms import OpenAI


load_dotenv()

def compile(request):
    return render(request, 'new.html')

@csrf_exempt
def generate_solidity_code(request):
    if request.method == 'POST':
        # Get the text data from the request body
        text_data = request.POST.get('text_data', '')
        lang = request.POST.get('selected_language', '')
        if not text_data:
            return HttpResponseBadRequest("Text data is required.")
        
        api_key = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(api_key=api_key)
        
        # Define the chat prompt template
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    f"You are a helpful AI to converting pseudo code into perfect {lang}."
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template(text_data)
            ]
        )
        
        # Define conversation memory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Create LLMChain instance
        conversation = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )
        
        # Predict output based on input
        code = conversation.predict(input=f"""give me the {lang} code for this pseudo code declar all of lisince and remove all of the print statements and give me the {lang} code""")

        llm = OpenAI(openai_api_key=os.environ['OPENAI_API_KEY'],temperature=0.6)
        text = f"Expalin the {code} clearly."
        explain = llm.predict(text)
        

        html_content = markdown.markdown(explain)
        # Return the sample solidity code as JSON response
        return JsonResponse({'solidity_code': code, 'explain':html_content})
    else:
        return HttpResponseBadRequest("Only POST requests are allowed.")
