"""Optional low-memory execution of the same MiniLM model for small hosts.

Uses the model author's ONNX export, identical tokenizer, masked mean pooling
and L2 normalization. Default deployments retain SentenceTransformer.
"""
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer


class OnnxEncoder:
    def __init__(self, model_name):
        if model_name not in {"all-MiniLM-L6-v2", "sentence-transformers/all-MiniLM-L6-v2"}:
            raise ValueError("ONNX backend currently supports all-MiniLM-L6-v2 only.")
        repo = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = Tokenizer.from_file(hf_hub_download(repo, "tokenizer.json"))
        self.tokenizer.enable_truncation(max_length=256)
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(hf_hub_download(repo, "onnx/model.onnx"),
                                           sess_options=options, providers=["CPUExecutionProvider"])

    def encode(self, texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False):
        single = isinstance(texts, str)
        values = [texts] if single else texts
        batches = []
        for start in range(0, len(values), batch_size):
            tokens = self.tokenizer.encode_batch(values[start:start + batch_size])
            inputs = {"input_ids": np.array([t.ids for t in tokens], dtype=np.int64),
                      "attention_mask": np.array([t.attention_mask for t in tokens], dtype=np.int64),
                      "token_type_ids": np.array([t.type_ids for t in tokens], dtype=np.int64)}
            names = {i.name for i in self.session.get_inputs()}
            hidden = self.session.run(None, {name: value for name, value in inputs.items() if name in names})[0]
            mask = inputs["attention_mask"][..., None]
            vectors = (hidden * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1)
            if normalize_embeddings:
                vectors /= np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)
            batches.append(vectors)
        result = np.concatenate(batches).astype(np.float32)
        return result[0] if single else result
