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
from base.models import MyModel


import os
import io
import zipfile
from django.http import HttpResponse


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
        model_data = MyModel(code=code,explain=explain)
        model_data.save()
        print(code, explain)
        # Return the sample solidity code as JSON response
        return JsonResponse({'solidity_code': code, 'explain':html_content})
    else:
        return HttpResponseBadRequest("Only POST requests are allowed.")



def compress_and_download_folder(request):
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    model = MyModel.objects.all()[::-1][0]
    with open("VaraBase/README.md", "w") as f:
        f.write(model.explain)
    with open("VaraBase/src/lib.rs", "w") as f:
        f.write(model.code)
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through the directory and add all files to the zip archive
        for foldername, _, filenames in os.walk("VaraBase"):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, "VaraBase")
                zip_file.write(filepath, arcname)

    # Create the HTTP response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="compressed_folder.zip"'
    return response
