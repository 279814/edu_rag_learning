# 导入标准库
import json
import os, sys
# 导入 PyTorch
import torch
# 导入日志
current_file = os.path.abspath(__file__)
model_dir_path = os.path.dirname(os.path.dirname(current_file))
project_root = os.path.dirname(model_dir_path)
sys.path.insert(0, project_root)

from base import logger
# 导入numpy
import numpy as np
# 导入 Transformers 库
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import Trainer, TrainingArguments
# 导入train_test_split
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix


class QueryClassifier:
    def __init__(self, model_path=os.path.join(model_dir_path, 'bert_query_classifier')):
        self.model_path = model_path
        # print(self.model_path)
        self.tokenizer = BertTokenizer.from_pretrained(os.path.join(model_dir_path, 'models', 'bert-base-chinese'))
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f'使用{self.device}设备')
        self.label_map = {"通用知识": 0, "专业咨询": 1}
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = BertForSequenceClassification.from_pretrained(self.model_path)
            logger.info(f'微调模型已加载：{self.model_path}')
            self.model.to(self.device)
        else:
            self.model = BertForSequenceClassification.from_pretrained(os.path.join(model_dir_path, 'models', 'bert-base-chinese'), num_labels=2)
            logger.info(f'初始化新 BERT 模型')
            self.model.to(self.device)

    def train_model(self, data_file=os.path.join(model_dir_path, 'classify_data', 'model_generic_5000.json')):
        """训练 BERT 分类模型"""
        # 加载数据集
        if not os.path.exists(data_file):
            logger.error(f"数据集文件 {data_file} 不存在")
            raise FileNotFoundError(f"数据集文件 {data_file} 不存在")
        with open(data_file, 'r', encoding='utf-8') as f:
            data = [json.loads(value) for value in f.readlines()]
        # print(data)
        texts = [item['query'] for item in data]
        labels = [item['label'] for item in data]
        # print(texts, labels)

        train_texts, eval_texts, train_labels, eval_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

        # 预处理
        train_encodings, train_labels = self.preprocess_data(train_texts, train_labels)
        eval_encodings, eval_labels = self.preprocess_data(eval_texts, eval_labels)
        # print(train_encodings)
        # print(train_labels)
        # print(train_encodings['input_ids'].shape)

        #创建Dataset
        train_dataset = self.create_dataset(train_encodings, train_labels)
        eval_dataset = self.create_dataset(eval_encodings, eval_labels)
        # print(len(train_dataset), len(eval_dataset))
        # print(train_dataset[0])

        # 设置训练参数
        training_args = TrainingArguments(
            output_dir=os.path.join(model_dir_path, 'bert_results'),
            num_train_epochs=2,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=50,
            weight_decay=0.01,
            logging_dir=os.path.join(model_dir_path, 'bert_logs'),
            logging_steps=10,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            save_total_limit=1,  # 只保存一个检查点
            metric_for_best_model="eval_loss",
            fp16=False,  # 禁用混合精度
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics
        )
        logger.info(f'开始训练模型')
        trainer.train()
        self.save_model()

        # 评估模型
        self.evaluate_model(eval_texts, eval_labels)


    def evaluate_model(self, texts, labels):
        """评估模型"""
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors="pt"
        )
        dataset = self.create_dataset(encodings, labels)
        trainer = Trainer(model=self.model)
        predictions = trainer.predict(dataset)
        pred_labels = np.argmax(predictions.predictions, axis=-1)
        true_labels = labels  # 直接使用数字标签

        logger.info("分类报告:")
        logger.info(classification_report(
            true_labels,
            pred_labels,
            target_names=["通用知识", "专业咨询"]
        ))
        logger.info("混淆矩阵:")
        logger.info(confusion_matrix(true_labels, pred_labels))

    def save_model(self):
        """保存模型"""
        self.model.save_pretrained(self.model_path)
        self.tokenizer.save_pretrained(self.model_path)
        logger.info(f"模型保存至: {self.model_path}")

    def compute_metrics(self, eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return {"accuracy": (predictions == labels).mean()}

    def create_dataset(self, encodings, labels):
        class MyDataSet(torch.utils.data.Dataset):
            def __init__(self, encodings, labels):
                self.encodings = encodings
                self.labels = labels

            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx])
                return item

            def __len__(self):
                return len(self.labels)
        return MyDataSet(encodings, labels)


    def preprocess_data(self, texts, labels):
        """预处理数据为 BERT 输入格式"""
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors="pt"
        )
        return encodings, [self.label_map[label] for label in labels]

    def predict_category(self, query):
        # 检查模型是否加载
        if self.model is None:
            # 模型未加载，记录错误
            logger.error("模型未训练或加载")
            # 默认返回通用知识
            return "通用知识"
        # 对查询进行编码（max_length 与训练时保持一致，均为 128，避免训推分布不一致）
        encoding = self.tokenizer(query, truncation=True, padding='max_length', max_length=128, return_tensors="pt")
        # 将编码移到指定设备
        encoding = {k: v.to(self.device) for k, v in encoding.items()}
        self.model.eval()
        # 不计算梯度，进行预测
        with torch.no_grad():
            # 获取模型输出
            outputs = self.model(**encoding)
            # 获取预测结果
            prediction = torch.argmax(outputs.logits, dim=1).item()
        # 根据预测结果返回类别
        return "专业咨询" if prediction == 1 else "通用知识"


if __name__ == '__main__':
    query_classifier = QueryClassifier()
    # query_classifier.train_model()
    result = query_classifier.predict_category("什么是AI")
    print(result)
    result = query_classifier.predict_category("AI学科的课程大纲是什么")
    print(result)









