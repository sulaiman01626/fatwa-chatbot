import google.generativeai as genai
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Gemini API কনফিগার
genai.configure(api_key="YOUR_API_KEY")  # ← তোমার API Key বসাও
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Gemini থেকে উত্তর আনার ফাংশন
def ask_gemini(question):
    prompt = f"""তুমি একজন ইসলামিক মুফতি। শরিয়তের আলোকে সংক্ষিপ্ত ও সহজ ভাষায় উত্তর দাও।

প্রশ্ন: {question}

উত্তর:"""
    response = model.generate_content(prompt)
    return response.text.strip()

# প্রশ্ন ডাটাবেজে খোঁজা, না পেলে Gemini কে জিজ্ঞাসা
def get_fatwa_answer(question):
    conn = sqlite3.connect("fatwa.db")
    cursor = conn.cursor()

    cursor.execute("SELECT answer FROM Fatwa WHERE question LIKE ?", ('%' + question + '%',))
    result = cursor.fetchone()
    conn.close()

    if result:
        return "📘 ডাটাবেস থেকে:\n" + result[0]
    else:
        return "🤖 Gemini থেকে:\n" + ask_gemini(question)

@app.post("/ask")
async def ask_fatwa(request: Request):
    data = await request.json()
    question = data.get("question", "")
    if not question:
        return JSONResponse({"error": "প্রশ্ন পাওয়া যায়নি"}, status_code=400)
    answer = get_fatwa_answer(question)
    return {"answer": answer}
