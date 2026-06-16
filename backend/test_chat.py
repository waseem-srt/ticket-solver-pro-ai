from rag.generator import get_llm_generator

llm = get_llm_generator()

print("Generator initialized. Running test...")
for token in llm.generate_stream(
    system_prompt="You are a helpful assistant.",
    user_message="Say hello!",
    history=[]
):
    print(token, end="", flush=True)

print("\nDone.")
