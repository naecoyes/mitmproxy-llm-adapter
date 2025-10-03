from mitmproxy import http
import json
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # 可用环境变量注入 [web:113]

def request(flow: http.HTTPFlow) -> None:
    # 确保 Host 指向 api.openai.com，必要时注入或覆盖 Authorization [web:113][web:107]
    if flow.request.host == "api.openai.com":
        if OPENAI_API_KEY and "authorization" not in flow.request.headers:
            flow.request.headers["authorization"] = f"Bearer {OPENAI_API_KEY}"  # 注入鉴权 [web:113][web:107]
        # 建议去掉上游压缩以简化调试
        flow.request.headers["accept-encoding"] = "identity"  # 可选 [web:113]

def response(flow: http.HTTPFlow) -> None:
    # 严格化 /v1/models 响应结构，保证 object=list 与 data=[...] 形态 [web:107][web:115]
    if flow.request.host == "api.openai.com" and flow.request.path.endswith("/v1/models"):
        try:
            patched = {
                "object": "list",
                "data": [
                    {"id": "gpt-4.1", "object": "model", "created": 0, "owned_by": "openai"},
                    {"id": "o1", "object": "model", "created": 0, "owned_by": "openai"}
                ]
            }
            flow.response.text = json.dumps(patched)
            flow.response.headers["content-type"] = "application/json"
        except Exception as e:
            # 保底不干扰上游响应
            pass
