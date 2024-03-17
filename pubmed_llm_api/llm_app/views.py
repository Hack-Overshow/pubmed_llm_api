from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from groq import Groq
import os

api_key=os.environ["GROK_API_KEY"]="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" 
client = Groq(api_key=api_key) 

# Function to prepare abstracts for LLM
def prepare_abstracts_for_llm(query, num_results):
    apiUrl = 'https://nirakar09.pythonanywhere.com/'
    params = {'query': query, 'num_results': num_results}
    response = requests.get(apiUrl, params=params)

    if response.status_code == 200:
        data = response.json()

        abstracts = []
        for result in data.get('results', []):
            abstract = result.get('Abstract', '')
            abstracts.append(abstract)

        llm_context = "\n\n".join(abstracts)
        return llm_context
    else:
        raise Exception(f"Request failed with status code: {response.status_code}")

# View to handle answering questions with abstracts
@csrf_exempt
def answer_question_with_abstracts(request):
    if request.method == 'POST':
        # Get data from POST request
        question = request.POST.get('question', '')
        query = request.POST.get('keywords', '')
        num_results = int(request.POST.get('num_results', 0))

        # Prepare abstracts for LLM
        abstracts = prepare_abstracts_for_llm(query, num_results)

        # Build prompt for LLM
        groq_prompt = f"""
        Your job is to answer the questions based on the given abstracts, you are a medical helper to the doctor, analysing the sypmtoms and providing preliminary care:

        Abstracts: {abstracts}

        Question: {question}
        Answer: """

        # Generate LLM response
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": groq_prompt}],
            model="mixtral-8x7b-32768"
        )

        # Return LLM response
        return JsonResponse({'answer': response.choices[0].message.content})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=400)
