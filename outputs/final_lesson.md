# Introduction to RAG

## 1. What it is
Imagine you are a student. You memorized many facts for your school exams. But sometimes, you forget where you read a specific fact. You open your notebook, find the right page, and use that fact to answer the question. 

**RAG** stands for **R**etrieval, **A**ugmented, **G**eneration. 
It is a clever trick that helps computers use two things together:
1. What the computer already knows (its built-in facts).
2. Extra information we supply to it.

This extra information is taken from real documents.

## 2. Why it is useful / What problem it solves
Computers can make mistakes called "hallucinations." A hallucination means the computer invents facts that are not true. 

Sometimes, a computer learns from old textbooks. By the time you use it, those books might be outdated. If you ask the computer a question, it might give you an old, wrong answer because it only remembers the old book. 

RAG solves this problem. It makes the computer always check its current library of documents before answering. This ensures the answer is based on your latest information.

To explain RAG simply, here are the main words:
*   **Retrieval**: Finding the right piece of information.
*   **Relevant information**: Just the exact facts we need from the documents. We don't give the computer all the documents; we only give the specific part it needs.
*   **Context**: The background situation or environment the computer uses to understand the information. 
*   **Generation**: The computer writing the final answer using the information it found.

## 3. Key parts
RAG is made of three simple parts:

1.  **The Searcher (Retrieval)**: This part looks at your question and finds the right document or facts. 
2.  **The Source Documents (Library)**: These are the files or pieces of information you want the computer to read. Examples: your school notes, a website, or a company email.
3.  **The Brain (Generation)**: This is the main computer model. It takes the information the Searcher finds, understands it with the Context, and writes a clear answer.

## 4. How it works step by step
Here is how RAG works when you ask a question:

1.  **You ask a question.** For example: "When did India gain independence?"
2.  **The Searcher looks for facts.** It searches your documents (like your textbook) and finds the part that mentions this date.
3.  **The computer gets the relevant information.** It only uses the exact sentence: "India got independence on August 15, 1947." It ignores all the other text in the book.
4.  **The Brain reads the context.** The computer thinks: "I know India is a country, and August 15 is a date."
5.  **The computer generates the answer.** It writes the final response: "India gained independence on August 15, 1947."

## 5. A worked example
Let us pretend you ask a computer a question about your favorite subject, Math. 

*   **Your Question**: "What is the formula for the area of a circle?"
*   **Your Document (Source)**: A piece of paper that says, "Area of a circle equals pi times the radius squared. Pi is 3.14."
*   **Step 1 (Retrieval)**: The Searcher finds your paper.
*   **Step 2 (Relevant information)**: The computer only keeps the part about the circle. 
*   **Step 3 (Context)**: The computer knows it is dealing with a circle and a formula.
*   **Step 4 (Generation)**: The computer writes the answer: "The area of a circle is 3.14 times the radius squared."

## 6. What it cannot do / Limitations
There are important things RAG cannot do:

*   **It does not train the computer.** When the computer looks at documents, it is just reading them. Looking at documents does not change the computer's brain weights. The computer's basic brain is the same before and after using RAG. It is just using the extra documents to help.
*   **It does not guarantee the answer is true.** If you give the computer a wrong document, or a fake document, RAG will give you a wrong answer. It just copies whatever it reads. 
*   **It only knows what you show it.** If you do not show it a document about a certain topic, it will not answer correctly. It cannot guess the answer by itself.

## 7. Short recap and self-check
**Recap**: 
*   RAG helps a computer use its own memory plus extra documents to give better answers.
*   The Searcher finds the right facts, and the Brain writes the answer.
*   Looking at documents does not make the computer smarter.
*   RAG can still give wrong answers if the documents are wrong.

**Self-check Questions**:
1.  Why do we use RAG? 
    *(Answer: To help the computer find the right facts and avoid giving wrong answers.)*
2.  Does looking at documents change how smart the computer is? 
    *(Answer: No, it just uses the documents to help answer the question.)*
3.  Can RAG guarantee that every answer it gives is true? 
    *(Answer: No, if the documents are wrong, the answer will also be wrong.)*