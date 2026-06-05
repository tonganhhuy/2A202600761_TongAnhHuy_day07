# Lab 3: Chatbot và ReAct Agent (Phiên bản Công nghiệp)

Chào mừng bạn đến với Giai đoạn 3 của khóa học Agentic AI! Lab này tập trung vào việc chuyển từ một chatbot LLM đơn giản sang một **ReAct Agent** hoàn chỉnh với khả năng giám sát và theo dõi theo tiêu chuẩn công nghiệp.

## 🚀 Bắt đầu

### 1. Thiết lập môi trường
Sao chép file `.env.example` thành `.env` và điền các API key của bạn:

```bash
cp .env.example .env
```

### 2. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

### 3. Cấu trúc thư mục

- `src/tools/`: Điểm mở rộng để bạn bổ sung các công cụ (tools) tùy chỉnh của riêng mình.

## 🏠 Chạy với mô hình cục bộ (CPU)

Nếu không muốn sử dụng OpenAI hoặc Gemini, bạn có thể chạy các mô hình mã nguồn mở (ví dụ: Phi-3) trực tiếp trên CPU bằng thư viện `llama-cpp-python`.

### 1. Tải mô hình

Tải mô hình **Phi-3-mini-4k-instruct-q4.gguf** (khoảng 2.2 GB) từ Hugging Face:

- Phi-3-mini-4k-instruct-GGUF: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
- Tải trực tiếp: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

### 2. Đặt mô hình vào dự án

Tạo thư mục `models/` ở thư mục gốc của dự án và di chuyển file `.gguf` đã tải vào đó.

### 3. Cập nhật file `.env`

Thay đổi `DEFAULT_PROVIDER` và thiết lập đường dẫn tới mô hình:

```env
DEFAULT_PROVIDER=local
LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
```

### 4. Chạy demo Vinpearl ReAct Agent

Sau khi đặt file GGUF vào vị trí được chỉ định bởi `LOCAL_MODEL_PATH`, chạy:

```bash
python run_vinpearl_agent.py
```

Demo này sử dụng mô hình cục bộ kết hợp với các công cụ (tools) mô phỏng của Vinpearl để:

- Tìm kiếm các gói dịch vụ.
- Lọc các gói có bao gồm VinWonders.
- Tạo lịch trình du lịch 3 ngày 2 đêm cho gói dịch vụ được chọn.

### 5. Chạy giao diện chatbot Vinpearl

Khởi động máy chủ chatbot cục bộ:

```bash
python vinpearl_chatbot_app.py
```

Mở trình duyệt và truy cập:

```text
http://127.0.0.1:8000
```

Giao diện sẽ hiển thị:

- Cuộc trò chuyện (chat).
- Tình trạng phòng hiện có.
- Giá phòng theo từng đêm.
- Trạng thái phòng theo từng ngày.
- Đặt phòng đang chờ xác nhận.
- Các đặt phòng đã được xác nhận.

Nếu `LOCAL_MODEL_PATH` trỏ tới một file GGUF hợp lệ, máy chủ sẽ sử dụng ReAct Agent chạy cục bộ.

Nếu mô hình chưa sẵn sàng, hệ thống sẽ tự động chuyển sang luồng đặt phòng cục bộ mang tính xác định (deterministic) để phục vụ việc kiểm thử.

Công cụ xác nhận đặt phòng được bảo vệ: một đặt phòng chỉ được hoàn tất khi người dùng chủ động xác nhận bằng các cụm từ như:

- confirm
- agree
- chốt đặt
- xác nhận đặt

## 🎯 Mục tiêu của Lab

1. **Chatbot cơ bản (Baseline Chatbot)**  
   Quan sát những hạn chế của một LLM thông thường khi phải xử lý các bài toán suy luận nhiều bước.

2. **Vòng lặp ReAct (ReAct Loop)**  
   Cài đặt chu trình `Thought → Action → Observation` trong file `src/agent/agent.py`.

3. **Chuyển đổi nhà cung cấp mô hình (Provider Switching)**  
   Chuyển đổi linh hoạt giữa OpenAI và Gemini thông qua giao diện `LLMProvider`.

4. **Phân tích lỗi (Failure Analysis)**  
   Sử dụng các log có cấu trúc trong thư mục `logs/` để xác định nguyên nhân thất bại của agent (ảo giác AI, lỗi phân tích cú pháp, v.v.).

5. **Chấm điểm & Điểm thưởng (Grading & Bonus)**  
   Làm theo hướng dẫn trong `SCORING.md` để tối đa hóa số điểm và khám phá các tiêu chí đánh giá nâng cao.

## 🛠️ Cách sử dụng bộ khung cơ sở (Baseline)

Mã nguồn được thiết kế như một **nguyên mẫu sản phẩm thực tế (Production Prototype)**. Dự án bao gồm:

- **Telemetry**: Mọi hành động đều được ghi lại dưới dạng JSON để phục vụ phân tích về sau.
- **Mẫu Provider mạnh mẽ**: Có thể dễ dàng mở rộng để hỗ trợ bất kỳ API LLM nào.
- **Khung mã nguồn rõ ràng**: Giúp bạn tập trung vào phần quan trọng nhất — logic suy luận của agent.

---

*Chúc bạn lập trình vui vẻ! Hãy cùng xây dựng những AI Agent thực sự hoạt động hiệu quả.*
