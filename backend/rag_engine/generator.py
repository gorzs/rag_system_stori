from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

MODEL_NAME = "google/flan-t5-base"

print("Loading model locally...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float32
)

# Create pipeline
llm = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512)

def generate_answer_local(question, context, history):
    prompt = f"""
You are a helpful assistant. Use the context and conversation history to answer the user's question.

Context:
{context}

Conversation History:
{history}

Question:
{question}

Answer:
""".strip()

    print("Final prompt sent to the model:")
    print(prompt)

    response = llm(prompt)[0]['generated_text']
    print("Generated response:")
    print(response)
    return response


def llm_should_escalate(question: str, answer: str) -> bool:
    prompt = f"""
You are an AI agent monitoring user conversations. 
If the assistant's answer is in one of the above cases:
 -is empty, unhelpful or incorrect
 -the user seems frustrated 
 -the user indicates that needs human help 
 -the user says that wants more help
Then, return YES. 
Otherwise, return NO.

Question: {question}
Answer: {answer}

Return only YES or NO.
""".strip()

    result = llm(prompt)[0]['generated_text'].strip().lower()
    print("Result of escalation validation:")
    print(result)
    return "yes" in result
