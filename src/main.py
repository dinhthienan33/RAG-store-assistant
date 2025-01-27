import google.generativeai as genai

genai.configure(api_key="AIzaSyAnygTCo3jUyXW8DMk52E0qI_07Qj60jJo")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)