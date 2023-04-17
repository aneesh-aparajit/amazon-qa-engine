import sys
from typing import Any, Dict, List

import pandas as pd
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

encoder = SentenceTransformer(
    'sentence-transformers/multi-qa-mpnet-base-cos-v1')

XLSX_PATH = ''


def get_most_similar_content(df: pd.DataFrame, query: str, top_k: int = 3) -> Dict[str, List[Any]]:
    query_emb = encoder.encode(query)
    doc_emb = encoder.encode(df['keys'].values)

    scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()
    doc_scores = list(zip(scores, list(enumerate(df['keys'].values))))
    doc_scores = sorted(doc_scores, key=lambda x: x[0], reverse=True)

    results = doc_scores[:top_k]

    result_dict = {
        'score': [],
        'idx': [],
        'doc': []
    }

    for score, (idx, doc) in results:
        result_dict['score'].append(score)
        result_dict['idx'].append(idx)
        result_dict['doc'].append(doc)

    return result_dict


def question_answering(documents: List[str], query: str):
    context = ''''''
    for document in documents:
        context += document
        context += "\n\n"

    question_answerer = pipeline(
        "question-answering", model='distilbert-base-cased-distilled-squad')
    result = question_answerer(question=query, context=context)
    return result['answer']


def process_query(query: str, df: pd.DataFrame):
    results = get_most_similar_content(df, query, top_k=2)
    documents = results['doc']
    output = question_answering(documents, query)
    return output


if __name__ == '__main__':
    query = sys.argv[1]
    df = pd.read_excel(XLSX_PATH)
    process_query(query=query, df=df)
