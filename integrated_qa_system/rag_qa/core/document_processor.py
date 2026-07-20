# core/document_processor.py

import os, sys
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownTextSplitter
from datetime import datetime

current_file = os.path.abspath(__file__)
model_path = os.path.dirname(os.path.dirname(current_file))
project_root = os.path.dirname(model_path)
sys.path.insert(0, model_path)
sys.path.insert(0, project_root)

from edu_text_spliter import AliTextSplitter, ChineseRecursiveTextSplitter
from edu_document_loaders import OCRPDFLoader, OCRDOCLoader, OCRPPTLoader, OCRIMGLoader
from base import logger, Config


conf = Config()
# 定义支持的文件类型及其对应的加载器字典
document_loaders = {
    # 文本文件使用 TextLoader
    ".txt": TextLoader,
    # PDF 文件使用 OCRPDFLoader
    ".pdf": OCRPDFLoader,
    # Word 文件使用 OCRDOCLoader
    ".docx": OCRDOCLoader,
    # PPT 文件使用 OCRPPTLoader
    ".ppt": OCRPPTLoader,
    # PPTX 文件使用 OCRPPTLoader
    ".pptx": OCRPPTLoader,
    # JPG 文件使用 OCRIMGLoader
    ".jpg": OCRIMGLoader,
    # PNG 文件使用 OCRIMGLoader
    ".png": OCRIMGLoader,
    # Markdown 文件使用 UnstructuredMarkdownLoader
    ".md": UnstructuredMarkdownLoader
}

# 定义函数，从指定文件夹加载多种类型文件并添加元数据, directory_path 是 一个学科的总文件夹(ai_data, java_data,...)
def load_documents_from_directory(directory_path):
    documents = []
    supported_extensions = document_loaders.keys()
    source = os.path.basename(directory_path).replace("_data", "")

    for root, sub_directories, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in supported_extensions:
                try:
                    loader_class = document_loaders[file_extension]
                    if file_extension == '.txt':
                        loader = loader_class(file_path, encoding='utf-8')
                    else:
                        loader = loader_class(file_path)
                    loaded_docs = loader.load()
                    for doc in loaded_docs:
                        doc.metadata["source"] = source
                        doc.metadata["file_path"] = file_path
                        doc.metadata["timestamp"] = datetime.now().isoformat()
                    documents.extend(loaded_docs)
                    # 记录成功加载文件的日志
                    logger.info(f"成功加载文件: {file_path}")
                except Exception as e:
                    # 记录加载失败的日志，包含错误信息
                    logger.error(f"加载文件 {file_path} 失败: {str(e)}")

            else:
                # 记录警告日志，提示不支持的文件类型
                logger.warning(f"不支持的文件类型: {file_path}")
    return documents


# 定义函数，处理文档并进行分层切分，返回子块结果
def process_documents(directory_path, parent_chunk_size=conf.PARENT_CHUNK_SIZE,
                     child_chunk_size=conf.CHILD_CHUNK_SIZE,
                     chunk_overlap=conf.CHUNK_OVERLAP):
    # 从指定目录加载所有文档
    documents = load_documents_from_directory(directory_path)
    # 记录加载的文档总数日志
    logger.info(f"加载的文档数量: {len(documents)}")

    # 初始化父块和子块分词器（通用）
    parent_splitter = ChineseRecursiveTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)
    # 初始化Markdown分词器
    markdown_parent_splitter = MarkdownTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    markdown_child_splitter = MarkdownTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)

    child_chunks = []
    for i, doc in enumerate(documents):
        file_extension = os.path.splitext(doc.metadata["file_path"])[1].lower()
        is_markdown = (file_extension == '.md')
        parent_splitter_to_use = markdown_parent_splitter if is_markdown else parent_splitter
        child_splitter_to_use = markdown_child_splitter if is_markdown else child_splitter
        logger.info(f"处理文档: {doc.metadata['file_path']}, 使用切分器: {'Markdown' if is_markdown else 'ChineseRecursive'}")

        parent_docs = parent_splitter_to_use.split_documents([doc])
        for j, parent_doc in enumerate(parent_docs):
            parent_id = f'doc_{i}_parent_{j}'
            sub_chunks = child_splitter_to_use.split_documents([parent_doc])
            for k, sub_chunk in enumerate(sub_chunks):
                # 为子块添加父块 ID 到元数据
                sub_chunk.metadata["parent_id"] = parent_id
                # 为子块添加父块内容到元数据
                sub_chunk.metadata["parent_content"] = parent_doc.page_content
                # 为子块生成唯一 ID，格式为 "parent_id_child_k"
                sub_chunk.metadata["id"] = f"{parent_id}_child_{k}"
                # 将子块添加到子块列表中
                child_chunks.append(sub_chunk)

    logger.info(f"处理完成，生成的子块数量: {len(child_chunks)}")
    return child_chunks




if __name__ == '__main__':
    chunks = process_documents(
        directory_path=r'E:\developdata\code\edu_rag_learning\integrated_qa_system\rag_qa\data\ai_data',
        parent_chunk_size=conf.PARENT_CHUNK_SIZE,
        child_chunk_size=conf.CHILD_CHUNK_SIZE,
        chunk_overlap=conf.CHUNK_OVERLAP
    )

    print(chunks[0])



