"""
MiMo大模型 API 客户端
基于Anthropic格式（Anthropic SDK）
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

import config


class MiMoClient:
    """MiMo API 客户端，基于Anthropic SDK"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = config.MIMO_API_KEY if api_key is None else api_key
        self.base_url = config.MIMO_BASE_URL if base_url is None else base_url
        self.model = config.MIMO_MODEL if model is None else model
        self._client: Optional[Any] = None

    @property
    def client(self) -> Any:
        """懒加载 Anthropic SDK 客户端实例"""
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    @client.setter
    def client(self, value: Any) -> None:
        self._client = value

    def _prepare_payload(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """分离 system 消息并构建 API 请求参数"""
        system_msgs: List[str] = []
        chat_messages: List[Dict[str, str]] = []
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "")
                if content:
                    system_msgs.append(content)
            else:
                chat_messages.append(msg)

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": config.MAX_TOKENS if max_tokens is None else max_tokens,
            "temperature": config.TEMPERATURE if temperature is None else temperature,
            "messages": chat_messages,
        }
        if system_msgs:
            kwargs["system"] = "\n\n".join(system_msgs)
        return kwargs

    @staticmethod
    def _format_api_error(exc: Exception, stream: bool = False) -> str:
        """统一格式化 API 异常信息"""
        prefix = "\n⚠️ " if stream else "⚠️ "
        try:
            import anthropic

            if isinstance(exc, anthropic.APIConnectionError):
                return f"{prefix}无法连接到MiMo API，请检查服务是否已启动。"
            if isinstance(exc, anthropic.APIStatusError):
                return f"{prefix}API调用出错（{exc.status_code}）：{exc.message}"
        except ImportError:
            pass
        return f"{prefix}API调用出错：{exc}"

    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Any:
        """发送聊天请求"""
        kwargs = self._prepare_payload(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if stream:
            return self._stream_request(kwargs)
        return self._normal_request(kwargs)

    def _normal_request(self, kwargs: Dict[str, Any]) -> str:
        """普通请求"""
        try:
            response = self.client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as exc:
            return self._format_api_error(exc, stream=False)

    def _stream_request(self, kwargs: Dict[str, Any]) -> Iterable[str]:
        """流式请求（生成器）"""
        try:
            with self.client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as exc:
            yield self._format_api_error(exc, stream=True)

    def test_connection(self) -> Tuple[bool, str]:
        """测试API连接"""
        try:
            result = self.chat([{"role": "user", "content": "你好，请回复OK"}])
            ok = isinstance(result, str) and not result.startswith("⚠️")
            return ok, result
        except Exception as exc:
            return False, str(exc)


# 全局客户端实例
_client: Optional[MiMoClient] = None


def get_client(**kwargs: Any) -> MiMoClient:
    """获取全局客户端实例"""
    global _client
    if _client is None:
        _client = MiMoClient(**kwargs)
    return _client


def reset_client() -> None:
    """重置客户端（更换配置后调用）"""
    global _client
    _client = None
