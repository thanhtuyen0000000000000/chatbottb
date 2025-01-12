from sentence_transformers import SentenceTransformer
import re
from docx import Document
from elasticsearch import Elasticsearch


# Kết nối với Elasticsearch (sử dụng localhost hoặc dịch vụ Elasticsearch)
es = Elasticsearch("http://localhost:9200")  # URL của Elasticsearch

def chunking_law_text(input_path):
    doc = Document(input_path)
    paragraphs = doc.paragraphs

    # Các từ khóa nhận diện chương, điều, và phần điều
    chapters = []
    current_chapter = None
    current_article = None
    current_clause = None

    for i, paragraph in enumerate(paragraphs):
        text = paragraph.text.strip()

        if not text:  # Bỏ qua các đoạn trống
            continue

        # Nhận diện chương: Ví dụ "Chương I", "Chương 1"
        if re.match(r'^\s*CHƯƠNG\s+[IVXLCDM\d]+(\.\d+)*', text):
            current_chapter = text
            chapter_title = paragraphs[i + 1].text.strip()
            chapters.append({'chapter': current_chapter, 'chapter_title': chapter_title, 'articles': []})
            current_article = None
            current_clause = None
        
        # Nhận diện điều: Ví dụ "Điều 1", "Điều 2"
        elif re.match(r'^\s*Điều\s+\d+', text):
            current_article = text
            if current_chapter:  # Nếu đã có chương, thêm vào danh sách
                chapters[-1]['articles'].append({'article': current_article, 'clauses': []})
            current_clause = None

        elif re.match(r'^\s*\d+\.', text):
            if current_article:  # Nếu đã có điều, thêm vào danh sách phần điều
                clause_content = re.sub(r'^\s*\d+\.\s*', '', text)
                chapters[-1]['articles'][-1]['clauses'].append(clause_content)
                current_clause = len(chapters[-1]['articles'][-1]['clauses']) - 1  # Theo dõi vị trí phần điều hiện tại

        # Ghép nối các đoạn văn tiếp theo vào điều khoản hiện tại
        elif current_clause is not None:
            # Thêm đoạn văn vào phần điều khoản hiện tại
            chapters[-1]['articles'][-1]['clauses'][current_clause] += f" {text}"

    return chapters

def save_to_elasticsearch(chunks, embedding_model):
    for chapter in chunks:
        for article in chapter['articles']:
            for clause in article['clauses']:
                # Tạo một ID duy nhất dựa trên chương, điều, và khoản
                embedding_vector = embedding_model.encode(clause).tolist()
                doc_id = f"{chapter['chapter']}_{article['article']}_{clause[:2]}".replace(" ", "_")
                
                doc = {
                    "embedding_vector": embedding_vector,
                    "metadata": {
                        "clause_text": clause,
                        "chapter": chapter['chapter'],
                        "chapter_title": chapter['chapter_title'],
                        "article": article['article']
                    }
                }
                # Lưu tài liệu với ID
                es.index(index="law_chunks", id=doc_id, document=doc)

def search_in_elasticsearch(query, embedding_model, es_client):
    # Tạo vector nhúng cho câu hỏi
    query_vector = embedding_model.encode(query).tolist()

    # Truy vấn Elasticsearch
    response = es_client.search(
        index="law_chunks",
        body={
            "size": 5,  # Số lượng kết quả cần trả về
            "query": {
                "script_score": {
                    "query": { "match_all": {} },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                        "params": { "query_vector": query_vector }
                    }
                }
            }
        }
    )
    return response['hits']['hits']

embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Sử dụng
chunks = chunking_law_text("52.2014.QH13_clean.docx")

# Lưu kết quả vào Elasticsearch
save_to_elasticsearch(chunks, embedding_model)
