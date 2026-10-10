from rag.qa import answer_question


question = "What are some popular places in South Goa?"


answer = answer_question(question)


print("\nQUESTION:")
print(question)

print("\nRAG ANSWER:")
print(answer)