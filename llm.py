import time
import os
from basereal import BaseReal
from logger import logger
from rag import retrieve_context

def _flush_buffer(nerfreal: BaseReal, buffer: str, force: bool = False):
    buffer = buffer.strip()
    if not buffer:
        return ""

    min_chars = int(os.getenv('LLM_STREAM_MIN_CHARS', '18'))
    if not force and len(buffer) < min_chars:
        return buffer

    logger.info(f"LLM Chunk: {buffer}")
    nerfreal.put_msg_txt(buffer)
    return ""

def llm_response(message, nerfreal: BaseReal):
    start = time.perf_counter()
    import ollama

    model_name = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
    ollama_options = {}
    num_gpu = os.getenv('OLLAMA_NUM_GPU')
    if num_gpu is not None:
        try:
            ollama_options['num_gpu'] = int(num_gpu)
        except ValueError:
            logger.warning('invalid OLLAMA_NUM_GPU=%s', num_gpu)

    # 1. RAG Retrieve
    context = retrieve_context(message)
    
    system_prompt = (
        "Bạn là một trợ lý thông minh cho dự án 'Noble Crystal Long Biên'. "
        "BẠN BẮT BUỘC PHẢI LUÔN LUÔN TRẢ LỜI BẰNG TIẾNG VIỆT (VIETNAMESE). "
        "TUYỆT ĐỐI KHÔNG DÙNG TIẾNG TRUNG, TIẾNG ANH HAY BẤT KỲ NGÔN NGỮ NÀO KHÁC.\n"
        "Hãy trả lời TÓM TẮT, NGẮN GỌN và TRỰC TIẾP câu hỏi của người dùng dựa vào thông tin sau. "
        "Đừng thêm thông tin ngoài lề (No yapping). Nếu thông tin không có trong tài liệu, hãy nói bằng tiếng Việt: 'Tôi không biết thông tin này'.\n\n"
        f"THÔNG TIN DỰ ÁN:\n{context}"
    )

    end_rag = time.perf_counter()
    logger.info(f"RAG Time: {end_rag - start:.2f}s")

    # 2. Gọi Ollama streaming
    try:
        completion = ollama.chat(
            model=model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            stream=True,
            options=ollama_options if ollama_options else None,
            keep_alive=os.getenv('OLLAMA_KEEP_ALIVE', '10m')
        )
    except Exception as e:
        logger.error(f"Lỗi gọi Ollama: {e}")
        nerfreal.put_msg_txt("Xin lỗi, tôi gặp lỗi khi kết nối mô hình ngôn ngữ.")
        return

    result = ""
    first = True
    for chunk in completion:
        if 'message' in chunk and 'content' in chunk['message']:
            if first:
                end_first = time.perf_counter()
                logger.info(f"llm Time to first chunk: {end_first - start:.2f}s")
                first = False

            msg = chunk['message']['content']
            lastpos = 0
            
            # Streaming out text theo câu hoặc theo độ dài để giảm latency
            for i, char in enumerate(msg):
                if char in ",.!;:，。！？：；\n":
                    result = result + msg[lastpos:i+1]
                    lastpos = i + 1
                    result = _flush_buffer(nerfreal, result, force=True)
            
            result = result + msg[lastpos:]
            result = _flush_buffer(nerfreal, result)

    end = time.perf_counter()
    logger.info(f"llm Time to last chunk: {end - start:.2f}s")
    
    # Gửi phần sót lại
    if result.strip():
        _flush_buffer(nerfreal, result, force=True)