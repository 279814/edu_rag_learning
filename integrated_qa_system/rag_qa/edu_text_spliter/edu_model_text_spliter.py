# from langchain.text_splitter import CharacterTextSplitter
from langchain_text_splitters.character import CharacterTextSplitter
import re
import sys
import types
from typing import List

# 兼容性 shim：transformers 5.x 已移除 transformers.onnx 模块，
# 而 modelscope 1.38.1 的 bert configuration 在 import 时需要 OnnxConfig 作为基类。
# 该基类在文档分割任务中并不会被实际调用，因此注入一个占位类即可让 import 通过。
if "transformers.onnx" not in sys.modules:
    try:
        from transformers.onnx import OnnxConfig  # noqa: F401  新版没有则走 except
    except ImportError:
        _onnx_stub = types.ModuleType("transformers.onnx")

        class OnnxConfig:  # 占位基类，仅供 import 期间的类定义使用
            pass

        _onnx_stub.OnnxConfig = OnnxConfig
        sys.modules["transformers.onnx"] = _onnx_stub

from modelscope.pipelines import pipeline

# 兼容性 shim：modelscope 1.38.1 的 pipeline builder 会强制向下透传
# trust_remote_code 参数，但 DocumentSegmentationTransformersPreprocessor
# 的构造函数并不接收该参数（且没有 **kwargs 兜底），导致 TypeError。
# 这里包裹其 __init__，过滤掉它不认识的关键字参数后再调用原始构造函数。
from modelscope.preprocessors.nlp import document_segmentation_preprocessor as _dsp

_orig_dsp_init = _dsp.DocumentSegmentationTransformersPreprocessor.__init__


def _patched_dsp_init(self, model_dir, model_max_length, *args, **kwargs):
    # 只保留原始构造函数支持的关键字参数，其余（如 trust_remote_code）丢弃
    allowed = {"mode", "question_column_name", "context_column_name",
               "example_id_column_name", "label_list"}
    filtered = {k: v for k, v in kwargs.items() if k in allowed}
    _orig_dsp_init(self, model_dir, model_max_length, *args, **filtered)


_dsp.DocumentSegmentationTransformersPreprocessor.__init__ = _patched_dsp_init


class AliTextSplitter(CharacterTextSplitter):
    def __init__(self, pdf: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.pdf = pdf

    def split_text(self, text: str) -> List[str]:
        # use_document_segmentation参数指定是否用语义切分文档，此处采取的文档语义分割模型为达摩院开源的nlp_bert_document-segmentation_chinese-base，论文见https://arxiv.org/abs/2107.09278
        # 如果使用模型进行文档语义切分，那么需要安装modelscope[nlp]：pip install "modelscope[nlp]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
        # 考虑到使用了三个模型，可能对于低配置gpu不太友好，因此这里将模型load进cpu计算，有需要的话可以替换device为自己的显卡id
        if self.pdf:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub(r'\s', " ", text)
            text = re.sub("\n\n", "", text)
        p = pipeline(
            task="document-segmentation",
            model=r'E:\developdata\code\edu_rag_learning\integrated_qa_system\rag_qa\models\nlp_bert_document-segmentation_chinese-base',
            device="cpu")
        result = p(documents=text)
        sent_list = [i for i in result["text"].split("\n\t") if i]
        return sent_list
if __name__ == '__main__':
    model_split = AliTextSplitter()
    result = model_split.split_text(text='移动端语音唤醒模型，检测关键词为“小云小云”。模型主体为4层FSMN结构，使用CTC训练准则，参数量750K，适用于移动端设备运行。模型输入为Fbank特征，输出为基于char建模的中文全集token预测，测试工具根据每一帧的预测数据进行后处理得到输入音频的实时检测结果。模型训练采用“basetrain + finetune”的模式，basetrain过程使用大量内部移动端数据，在此基础上，使用1万条设备端录制安静场景“小云小云”数据进行微调，得到最终面向业务的模型。后续用户可在basetrain模型基础上，使用其他关键词数据进行微调，得到新的语音唤醒模型，但暂时未开放模型finetune功能。')
    print(result)