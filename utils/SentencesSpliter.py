import gc

import spacy
from loguru import logger

from core.ConfigProvider import Spacy


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
    nlp = None

    @classmethod
    def load_model(cls) -> bool:
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
        if cls.nlp is None:
            try:
                cls.nlp = spacy.load(Spacy.MODEL)
            except Exception as e:
                logger.error(f"Failed to load model: {Spacy.MODEL}, {e}")
                return False
        return True

    @classmethod
    def split_text(cls, texts: str) -> list:
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
        if cls.nlp is None:
            logger.error("SpaCy模型未加载")
            return []

        doc = cls.nlp(texts)
        _sentences = [sent.text for sent in doc.sents]
        return _sentences

    @classmethod
    def release_model(cls) -> None:
        """
        释放加载的spaCy模型以释放资源。

        returns
        -------
        None
        """
        if cls.nlp is not None:
            cls.nlp = None
            gc.collect()  # 手动触发垃圾回收
            logger.info("SpaCy模型已释放")
