from mitmproxy import http, ctx
import json

MODEL_MAP = {
    "gpt-4.1-mini": "llama3.1:latest",
    "gpt-4o-mini": "qwen3-coder:latest",
}

class BodyRewriter:
    def __init__(self):
        # 以流 ID 记录聚合的请求体
        self.buffers = {}

    def requestheaders(self, flow: http.HTTPFlow):
        # 禁用压缩便于可读
        flow.request.headers["accept-encoding"] = "identity"
        # 仅处理目标路径
        if flow.request.path.endswith("/v1/chat/completions"):
            # 标记需要拦截聚合
            flow.request.stream = True

    def request(self, flow: http.HTTPFlow):
        # 当没有标记 stream 时，仍可能走到这里（非流式请求）
        if flow.request.path.endswith("/v1/chat/completions"):
            if flow.request.stream:
                return  # 流式场景交给 streaming 事件
            self._rewrite_now(flow)

    def requestchunk(self, flow: http.HTTPFlow):
        # 对于流式请求，每个 chunk 到达时被调用
        fid = id(flow)
        self.buffers.setdefault(fid, b"")
        # 追加本次分块
        if flow.request.raw_content:
            self.buffers[fid] += flow.request.raw_content
            flow.request.raw_content = b""  # 清空，等待全部聚合后再注入

    def requestend(self, flow: http.HTTPFlow):
        # 流式请求体接收完毕，在此统一改写并注入
        if flow.request.path.endswith("/v1/chat/completions"):
            fid = id(flow)
            raw = self.buffers.pop(fid, b"")
            try:
                text = raw.decode("utf-8", "replace")
            except Exception:
                text = ""
            if text:
                try:
                    data = json.loads(text)
                except Exception:
                    data = None
                if isinstance(data, dict):
                    old_model = data.get("model")
                    if old_model in MODEL_MAP:
                        data["model"] = MODEL_MAP[old_model]
                        new_text = json.dumps(data, ensure_ascii=False)
                        flow.request.text = new_text
                        ctx.log.info(f"Model remapped(stream): {old_model} -> {data['model']}")
                    else:
                        flow.request.text = text  # 原样注入
                        ctx.log.info(f"No remap(stream) for model: {old_model}")
                else:
                    flow.request.text = text  # 非 JSON，原样注入

    def _rewrite_now(self, flow: http.HTTPFlow):
        body = flow.request.get_text(strict=False) or ""
        if not body and flow.request.raw_content:
            try:
                body = flow.request.raw_content.decode("utf-8", "replace")
            except Exception:
                body = ""
        if not body:
            ctx.log.info("No request body (non-stream); skip mapping")
            return
        try:
            data = json.loads(body)
        except Exception:
            ctx.log.info("Body not JSON (non-stream); skip mapping")
            return
        if not isinstance(data, dict):
            ctx.log.info("Body not object (non-stream); skip mapping")
            return
        old_model = data.get("model")
        if old_model in MODEL_MAP:
            data["model"] = MODEL_MAP[old_model]
            flow.request.text = json.dumps(data, ensure_ascii=False)
            ctx.log.info(f"Model remapped: {old_model} -> {data['model']}")
        else:
            ctx.log.info(f"No remap for model: {old_model}")

addons = [BodyRewriter()]
