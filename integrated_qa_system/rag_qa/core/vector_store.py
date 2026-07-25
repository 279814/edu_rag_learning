from milvus_model.hybrid import BGEM3EmbeddingFunction
from pymilvus import MilvusClient, DataType, AnnSearchRequest, WeightedRanker
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
import hashlib
import os, sys, torch
import numpy as np

current_file = os.path.abspath(__file__)
module_dir = os.path.dirname(os.path.dirname(current_file))
project_root = os.path.dirname(module_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, module_dir)

from base import logger, Config
from core import process_documents
conf = Config()


# core/vector_store.py
# 定义 VectorStore 类，封装向量存储和检索功能
class VectorStore:
    # 初始化方法，设置向量存储的基本参数
    def __init__(self,
                 collection_name=conf.MILVUS_COLLECTION_NAME,
                 host=conf.MILVUS_HOST,
                 port=conf.MILVUS_PORT,
                 user=conf.MILVUS_USER,
                 password=conf.MILVUS_PASSWORD,
                 database=conf.MILVUS_DATABASE_NAME):

        # 设置 Milvus 集合名称
        self.collection_name = collection_name
        # 设置 Milvus 主机地址
        self.host = host
        # 设置 Milvus 端口号
        self.port = port
        # 设置 Milvus 用户名
        self.user = user
        # 设置 Milvus 密码
        self.password = password
        # 设置 Milvus 数据库名称
        self.database = database
        # 设置日志记录器
        self.logger = logger
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f'使用 {device} 设备')
        # 初始化 BGE-Reranker 模型，用于重排序检索结果
        self.reranker = CrossEncoder(os.path.join(module_dir, 'models', 'bge-reranker-large'), device=device)
        # 初始化 BGE-M3 嵌入函数，使用 CPU 设备，不启用 FP16
        self.embedding_function = BGEM3EmbeddingFunction(model_name_or_path=os.path.join(module_dir, 'models', 'bge-m3'), use_fp16=(device=='cuda'), device=device)
        # 获取稠密向量的维度
        self.dense_dim = self.embedding_function.dim["dense"]
        # 初始化 Milvus 客户端，连接到指定主机和数据库
        self.client = MilvusClient(uri=f"http://{self.host}:{self.port}", user=self.user, password=self.password, db_name=self.database)
        # 调用方法创建或加载 Milvus 集合
        self._create_or_load_collection()

    # 类私有化方法
    def _create_or_load_collection(self):
        # 检查指定集合是否已经存在
        if not self.client.has_collection(self.collection_name):
            # 创建集合 Schema，禁用自动 ID，启用动态字段
            schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
            # 添加 ID 字段，作为主键，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=100)
            # 添加文本字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            # 添加稠密向量字段，FLOAT_VECTOR 类型，维度由嵌入函数指定
            schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT16_VECTOR, dim=self.dense_dim)
            # 添加稀疏向量字段，SPARSE_FLOAT_VECTOR 类型
            schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
            # 添加父块 ID 字段，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="parent_id", datatype=DataType.VARCHAR, max_length=100)
            # 添加父块内容字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="parent_content", datatype=DataType.VARCHAR, max_length=65535)
            # 添加学科类别字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=50)
            # 添加时间戳字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="timestamp", datatype=DataType.VARCHAR, max_length=50)

            # 创建索引参数对象
            index_params = self.client.prepare_index_params()
            # 为稠密向量字段添加 IVF_FLAT 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="dense_vector",
                index_name="dense_index",
                index_type="IVF_FLAT",
                metric_type="IP",
                params={"nlist": 128}
            )
            # 为稀疏向量字段添加 SPARSE_INVERTED_INDEX 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="sparse_vector",
                index_name="sparse_index",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="IP",
                params={"drop_ratio_build": 0.2}
            )

            # 创建 Milvus 集合，应用定义的 Schema 和索引参数
            self.client.create_collection(collection_name=self.collection_name, schema=schema,
                                          index_params=index_params)
            # 记录创建集合的日志
            logger.info(f"已创建集合 {self.collection_name}")
        # 如果集合已存在
        else:
            # 记录加载集合的日志
            logger.info(f"已加载集合 {self.collection_name}")
        # 将集合加载到内存，确保可立即查询
        self.client.load_collection(self.collection_name)

    def add_documents(self, documents):
        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_function(texts)
        data = []

        for i, doc in enumerate(documents):
            text_hash = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
            sparse_vector = {}
            row = embeddings['sparse'][i]
            # print(row)
            indices = row.coords[0].tolist()
            values = row.data
            # print(indices, values)
            for index, value in zip(indices, values):
                sparse_vector[index] = value
            # print(sparse_vector)
            data.append({
                "id": text_hash,
                "text": doc.page_content,
                "dense_vector": np.asarray(embeddings["dense"][i], dtype=np.float16),
                "sparse_vector": sparse_vector,
                "parent_id": doc.metadata["parent_id"],
                "parent_content": doc.metadata["parent_content"],
                "source": doc.metadata.get("source", "unknown"),
                "timestamp": doc.metadata.get("timestamp", "unknown")
            })
            # 检查是否有数据需要插入
        if data:
            # 使用 upsert 操作插入数据，覆盖重复 ID
            self.client.upsert(collection_name=self.collection_name, data=data)
            # 记录插入或更新的文档数量日志
            logger.info(f"已向Milvus数据库插入或更新 {len(data)} 个文档")

    # 定义方法，执行混合检索并重排序
    def hybrid_search_with_rerank(self, query, k=conf.RETRIEVAL_K, source_filter=None):
        # 使用 BGE-M3 嵌入函数生成查询的嵌入
        query_embeddings = self.embedding_function([query])

        # 确保稠密向量是float32类型的numpy数组
        dense_vector = np.asarray(query_embeddings["dense"][0], dtype=np.float16)

        # 获取查询的稠密向量
        dense_query_vector = dense_vector
        # 初始化查询的稀疏向量字典
        sparse_query_vector = {}
        # 获取查询稀疏向量的第 0 行数据
        row = query_embeddings["sparse"][0]
        # 获取稀疏向量的非零值索引
        indices = row.coords[0].tolist()
        # 获取稀疏向量的非零值
        values = row.data
        # 将索引和值配对，填充稀疏向量字典
        for idx, value in zip(indices, values):
            sparse_query_vector[idx] = value

        # 初始化过滤表达式，默认不过滤
        filter_expr = f"source == '{source_filter}'" if source_filter else ""
        # 创建稠密向量搜索请求
        dense_request = AnnSearchRequest(
            data=[dense_query_vector],
            anns_field="dense_vector",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=k,
            expr=filter_expr
        )
        # 创建稀疏向量搜索请求
        sparse_request = AnnSearchRequest(
            data=[sparse_query_vector],
            anns_field="sparse_vector",
            param={"metric_type": "IP", "params": {}},
            limit=k,
            expr=filter_expr
        )

        # 创建加权排序器，稀疏向量权重 0.7，稠密向量权重 1.0
        ranker = WeightedRanker(1.0, 0.7)
        # 执行混合搜索，返回 Top-K 结果
        results = self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[dense_request, sparse_request],
            ranker=ranker,
            limit=k,
            output_fields=["text", "parent_id", "parent_content", "source", "timestamp"]
        )[0]

        # 将搜索结果转换为 Document 对象列表
        sub_chunks = [self._doc_from_hit(hit["entity"]) for hit in results]
        self.logger.info(f"混合检索得到 {len(sub_chunks)} 个子块")
        # 从子块中提取去重的父文档
        parent_docs = self._get_unique_parent_docs(sub_chunks)
        # 仅剩 0/1 个文档时无需重排序（≥2 个即交给 reranker 排序，选取数量由 CANDIDATE_M 决定）
        if len(parent_docs) <= 1:
            return parent_docs
            # 如果有父文档，进行重排序
        if parent_docs:
            # 创建查询与文档内容的配对列表
            pairs = [[query, doc.page_content] for doc in parent_docs]
            # 使用 BGE-Reranker 计算每个配对的得分
            scores = self.reranker.predict(pairs)
            # 根据得分从高到低排序文档
            ranked_parent_docs = [doc for _, doc in sorted(zip(scores, parent_docs), reverse=True)]
        # 如果没有父文档，返回空列表
        else:
            ranked_parent_docs = []

        # 返回前 k 个重排序后的文档
        return ranked_parent_docs[:conf.CANDIDATE_M]

    # 定义私有方法，从 Milvus 查询结果创建 Document 对象
    def _doc_from_hit(self, hit):
        # 创建并返回 Document 对象，填充内容和元数据
        return Document(
            page_content=hit.get("text"),
            metadata={
                "parent_id": hit.get("parent_id"),
                "parent_content": hit.get("parent_content"),
                "source": hit.get("source"),
                "timestamp": hit.get("timestamp")
            }
        )

    # 定义私有方法，从子块中提取去重的父文档
    def _get_unique_parent_docs(self, sub_chunks):
        # 初始化集合，用于存储已处理的父块内容（去重）
        parent_contents = set()
        # 初始化列表，用于存储唯一父文档
        unique_docs = []
        # 遍历所有子块
        for chunk in sub_chunks:
            # 获取子块的父块内容，默认为子块内容
            parent_content = chunk.metadata.get("parent_content", chunk.page_content)
            # 检查父块内容是否非空且未重复
            if parent_content and parent_content not in parent_contents:
                # 创建新的 Document 对象，包含父块内容和元数据
                unique_docs.append(Document(page_content=parent_content, metadata=chunk.metadata))
                # 将父块内容添加到去重集合
                parent_contents.add(parent_content)
        # 返回去重后的父文档列表
        return unique_docs


if __name__ == "__main__":
    vector_store = VectorStore()
    # documents = []
    # # documents.append(Document(page_content="This is a test document.", metadata={"parent_id": "123", "parent_content": "This is a test parent content.", "source": "test", "timestamp": "2023-04-01T12:00:00Z"}))
    # # 加载数据目录
    # data_dir = os.path.join(module_dir, 'data')
    # root, dirs, files = next(os.walk(data_dir))
    # for dir in dirs:
    #     documents.extend(process_documents(directory_path=os.path.join(data_dir, dir)))
    #
    # # 添加文档到向量存储
    # vector_store.add_documents(documents)
    query = "什么是神经网络？"
    result = vector_store.hybrid_search_with_rerank(query=query, source_filter='ai')
    print(result)
    print(len(result))
