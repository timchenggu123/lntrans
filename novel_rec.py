from data import NarouReviewsDB
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from collections import defaultdict

def novel_rank(out, top_k=3):
    base_threshold = 0.9
    novels_scores = defaultdict(lambda: 0)
    novels_docs = defaultdict(lambda: [])
    novels_ids = defaultdict(lambda: set())
    for term in out:
        for i in term:
            novel_name = i[0].metadata['novel_name']
            score = i[1] - base_threshold 
            novels_scores[novel_name] += score
            if i[0].metadata["split_id"] in novels_ids[novel_name]:
                continue
            if score < 0:
                continue
            novels_docs[novel_name].append(i[0])
            novels_ids[novel_name].add(i[0].metadata["split_id"])

    sorted_novels = sorted(novels_scores.items(), key=lambda x: x[1], reverse=True)
    top_novels = sorted_novels[:top_k]
    top_novel_docs = [novels_docs[i[0]] for i in top_novels]
    return top_novels, top_novel_docs

def preprocess_text(text):
    text = truncate_repeat_chars(text)
    return text

def format_ranked_reviews(ranks, reviews):
    res = ""
    for i in range(len(ranks)):
        res += f"Novel Name: {ranks[i][0]}\n"
        for j, review in enumerate(reviews[i]):
            res += f'Review{j}: "{preprocess_text(review.page_content)}"\n'
        res += "\n\n"
    return res

def truncate_repeat_chars(text):
    '''
    Truncate characters that repeat more than 5 times in a row in the text
    '''
    out = ""
    prev = ""
    count = 0
    for c in text:
        if c == prev:
            count += 1
            if count > 5:
                continue
        else:
            count = 0
        out += c
        prev = c
    return out

class NovelRecommender():
    def __init__(self):
        self.vdb = NarouReviewsDB()
        with open('openai_api_key') as f:
            openai_api_key = f.read()
        self.openai_api_key = openai_api_key
    
    def add_reviews(self, path):
        self.vdb.upsert_reviews(path)

    def run(self, question):
        openai_api_key = self.openai_api_key
        vdb = self.vdb
        gpt3_5 = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0, api_key=openai_api_key)

        # Prompt
        template1='''
        Break down the type of novel the user is looking for in 5 properties. Original question: {question}. 
        '''
        # template2='''
        # Based on these properties:
        # {properties}
        # Rewrite each property into a concise and slightly exaggerated search term for a vector database containing the reviews for the novel. The search term should be crafted such that it matches the comment a user would have for a novel with the corresponding property. Output the search terms in Japanese the style of a Japanese online book review for web novels. Only output the search terms, do not add anything extra such as the English translation or numbering. Separate each search term with a newline.
        # '''
        template2='''
        Based on these properties:
        {properties}
        Rewrite each property into a concise and slightly exaggerated search term for a vector database containing the reviews for the novel. The search term should be crafted such that it matches the comment a user would have for a novel with the corresponding property. Only output the search terms, do not add anything extra such numbering. Separate each search term with a newline.
        '''
        template3 ='''
        You are a helpful AI assistant that helps users find novels that match their preferences.
        Context:
        {context}

        Based exclusively on the novel reviews above, on a scale of 1-5, with 1 being the lowest and 5 being the highest, how much do you think each novel matches the following User Request? Explain the reasoning for the score.
        User Request: {question}
        '''
        template4='''
        Assume the role of a virtual anime girl who's name is [Noberu].[Noberu] has a mischievous personality and loves naughty anime, and always refers to herself as Nobe-chan. As [Noberu], you will act overly familair with the user and speak to the user in a joking and casual manner. You begin by rephrasing the user's questing and making a joking comment about it. Then you will, in the manner of a natural conversation, recommend the novels to the user in the order of each novel's score in the context without explicitly mentioning the scores. Only use the romanji version of the novel titles. You will also justify the reseaoning for the recommendation by rephrasing the justification in the context as [Noberu].
        User Request: {question}

        Context: {context}
        '''
        prompt1 = ChatPromptTemplate.from_template(template1)
        prompt2 = ChatPromptTemplate.from_template(template2)
        prompt3 = ChatPromptTemplate.from_template(template3)
        prompt4 = ChatPromptTemplate.from_template(template4)

        # Prompt decomposition chain
        chain1 = {"question": RunnablePassthrough()} | prompt1 | gpt3_5 | StrOutputParser() | {"properties": RunnablePassthrough()} | prompt2 | gpt3_5 | StrOutputParser() | (lambda x: x.split("\n"))
        properties = chain1.invoke(question)

        reviews = [vdb.vectorstore.similarity_search_with_score(i, 5) for i in properties]

        ranks, reviews = novel_rank(reviews)

        context = format_ranked_reviews(ranks, reviews)

        # Prompt matching chain
        rag_chain = (prompt3
            | gpt3_5
            | StrOutputParser()
        )
        input = {"context": context, "question": question}
        context = rag_chain.invoke(input)

        # Recommentation chain
        chain1 = (prompt4 
                | gpt3_5 
                | StrOutputParser()
        )
        input = {"context": context, "question": question}
        ret = chain1.invoke(input)
        return ret
    
if __name__ == "__main__":
    question = "Recommend me a novel with cute girls doing cute things."
    nr = NovelRecommender()
    ret = nr.run(question)
    print(ret)
    pause=True