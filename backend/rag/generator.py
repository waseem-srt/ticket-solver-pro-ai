from __future__ import annotations

from functools import lru_cache
from typing import AsyncIterator

from huggingface_hub import InferenceClient

from core.config import settings


@lru_cache(maxsize=1)
def _get_client() -> InferenceClient:
    """Singleton HuggingFace Inference client."""
    return InferenceClient(
        model=settings.hf_model_repo,
        token=settings.hf_token,
    )


import threading

_local_pipeline_cache = None
_load_lock = threading.Lock()


def is_local_model_loaded() -> bool:
    """Check if the local HuggingFace pipeline is loaded into memory."""
    global _local_pipeline_cache
    return _local_pipeline_cache is not None


def load_local_pipeline():
    """Load local HuggingFace model and tokenizer."""
    global _local_pipeline_cache
    with _load_lock:
        if _local_pipeline_cache is not None:
            return _local_pipeline_cache

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    model_id = settings.hf_model_repo
    print(f"Loading local model: {model_id} (this may take a few minutes on first run)...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # Select appropriate dtype based on GPU availability
    if torch.cuda.is_available():
        torch_dtype = torch.float16
        device_map = "auto"
    else:
        torch_dtype = torch.float32
        device_map = None  # defaults to CPU
        
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        device_map=device_map,
    )
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )
    _local_pipeline_cache = (pipe, tokenizer)
    return _local_pipeline_cache


def _get_local_pipeline():
    return load_local_pipeline()


class LLMGenerator:
    """
    Wraps local HuggingFace pipeline OR InferenceClient for chat completions
    based on config settings.
    """

    def __init__(self) -> None:
        if not settings.run_local_llm:
            self.client = _get_client()
        else:
            self.client = None
        self.model = settings.hf_model_repo

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict] | None = None,
        max_new_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        """Synchronous generation — returns full response string."""
        if settings.run_local_llm:
            pipe, tokenizer = _get_local_pipeline()
            messages = self._build_messages(system_prompt, user_message, history)
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            outputs = pipe(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0.0,
                pad_token_id=tokenizer.eos_token_id,
            )
            generated_text = outputs[0]["generated_text"]
            return generated_text[len(prompt):].strip()
        else:
            messages = self._build_messages(system_prompt, user_message, history)
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_new_tokens,
                temperature=temperature,
                stream=False,
            )
            return response.choices[0].message.content.strip()

    def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict] | None = None,
        max_new_tokens: int = 1024,
        temperature: float = 0.3,
    ):
        """Synchronous streaming generator — yields token strings."""
        if settings.run_local_llm:
            pipe, tokenizer = _get_local_pipeline()
            messages = self._build_messages(system_prompt, user_message, history)
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            from transformers import TextIteratorStreamer
            from threading import Thread

            streamer = TextIteratorStreamer(
                tokenizer, skip_prompt=True, skip_special_tokens=True, clean_up_tokenization_spaces=True
            )
            
            inputs = tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(pipe.model.device) for k, v in inputs.items()}
            
            generation_kwargs = dict(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0.0,
                pad_token_id=tokenizer.eos_token_id,
                streamer=streamer,
            )
            
            thread = Thread(target=pipe.model.generate, kwargs=generation_kwargs)
            thread.start()
            
            for new_text in streamer:
                yield new_text
        else:
            messages = self._build_messages(system_prompt, user_message, history)
            stream = self.client.chat_completion(
                messages=messages,
                max_tokens=max_new_tokens,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict] | None,
    ) -> list[dict]:
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages


@lru_cache(maxsize=1)
def get_llm_generator() -> LLMGenerator:
    return LLMGenerator()
