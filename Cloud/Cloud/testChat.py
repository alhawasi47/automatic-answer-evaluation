import openai
print("API Key:", openai.api_key)
# Set your OpenAI API key
openai.api_key = ''

# Example prompt
prompt = "What is the capital of France?"

# Make an API call to ChatGPT
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    max_tokens=100
)

# Print the generated response
print(response['choices'][0]['text'])
