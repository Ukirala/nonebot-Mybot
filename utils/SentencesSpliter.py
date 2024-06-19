import gc

import spacy
from loguru import logger


class SentencesSpliter:
    """
    用于加载spaCy模型并将文本分割为句子的类

    Parameters
    ----------
    self.nlp : spacy.language.Language 或 None
        spaCy语言模型，用于处理文本。初始为 None。

    returns
    -------
    load_model(model_name: str) -> bool
        加载指定名称的spaCy模型。
    split_text(texts: str) -> list
        将输入文本分割为句子。
    release_model() -> None
        释放spaCy模型以释放资源。
    """

    def __init__(self):
        """初始化"""
        self.nlp = None

    def load_model(self, model_name: str) -> bool:
        """
        加载指定名称的spaCy模型。

        Parameters
        ----------
        model_name : str
            要加载的spaCy模型名称。

        returns
        -------
        bool
            如果模型加载成功，返回 True；否则返回 False。
        """
        if self.nlp is None:
            try:
                self.nlp = spacy.load(model_name)
            except Exception as e:
                logger.error(f"无法加载SpaCy模型: {model_name}, {e}")
                return False
        return True

    def split_text(self, texts: str) -> list:
        """
        使用加载的spaCy模型将输入文本分割为句子。

        Parameters
        ----------
        texts : str
            要分割为句子的输入文本。

        returns
        -------
        list
            从输入文本中提取的句子列表。如果未加载模型，则返回空列表。
        """
        if self.nlp is None:
            logger.error("SpaCy模型未加载")
            return []

        doc = self.nlp(texts)
        _sentences = [sent.text for sent in doc.sents]
        return _sentences

    def release_model(self) -> None:
        """
        释放加载的spaCy模型以释放资源。

        returns
        -------
        None
        """
        if self.nlp is not None:
            self.nlp = None
            gc.collect()  # 手动触发垃圾回收
            logger.info("SpaCy模型已释放")

