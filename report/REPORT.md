# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Tống Anh Huy
**Nhóm:** C401-B2
**Ngày:** 2026-06-05

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity (độ tương đồng cosine cao, gần bằng 1.0) nghĩa là hai vector biểu diễn văn bản hướng về cùng một phía trong không gian vector đa chiều, thể hiện rằng hai văn bản đó có sự tương đồng lớn về mặt ngữ nghĩa, mặc dù chúng có thể sử dụng các từ ngữ khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: "Học máy là một phân nhánh của trí tuệ nhân tạo tập trung vào việc học từ dữ liệu."
- Sentence B: "Machine learning là một lĩnh vực của AI giúp các hệ thống tự động rút ra tri thức từ thông tin đầu vào."
- Tại sao tương đồng: Hai câu này diễn đạt cùng một khái niệm cốt lõi (Machine Learning thuộc AI và học từ dữ liệu) bằng cách sử dụng các từ ngữ khác nhau (song ngữ Anh - Việt, cấu trúc câu khác biệt), nhưng mô hình embedding nắm bắt được ngữ nghĩa đồng nhất nên có độ tương đồng cosine rất cao.

**Ví dụ LOW similarity:**
- Sentence A: "Tôi muốn đặt một phòng khách sạn tại Vinpearl Nha Trang vào ngày mai."
- Sentence B: "Trực quan hóa quy trình thủ công giúp phát hiện các nút thắt cổ chai trong hệ thống."
- Tại sao khác: Hai câu này đề cập đến hai chủ đề hoàn toàn không liên quan (đặt phòng du lịch tại Vinpearl vs. tối ưu hóa quy trình nghiệp vụ phần mềm), do đó các vector biểu diễn của chúng hướng về các phía khác nhau trong không gian biểu diễn ngữ nghĩa, dẫn đến độ tương đồng cosine thấp (gần 0 hoặc âm).

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ đo góc giữa hai vector mà không phụ thuộc vào độ dài (magnitude) của vector, do đó nó không bị ảnh hưởng bởi độ dài của văn bản (số lượng từ). Euclidean distance đo khoảng cách tuyệt đối nên các văn bản có cùng nội dung nhưng độ dài khác nhau sẽ bị coi là xa nhau, làm giảm độ chính xác của mô hình NLP.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Áp dụng công thức: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
> Ta có:
> `num_chunks = ceil((10000 - 50) / (500 - 50))`
> `num_chunks = ceil(9950 / 450)`
> `num_chunks = ceil(22.111...)`
> `num_chunks = 23`
> *Đáp án:* 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> - Thay đổi chunk count: Khi tăng overlap lên 100, bước nhảy (stride) giảm xuống còn 400. Số lượng chunk tăng lên thành `ceil((10000 - 100) / 400) = ceil(9900 / 400) = ceil(24.75) = 25` chunks.
> - Tại sao muốn overlap nhiều hơn: Tăng overlap giúp bảo toàn tốt hơn các ngữ cảnh nằm ở ranh giới giữa các chunk liền kề, ngăn chặn tình trạng mất thông tin hoặc đứt gãy ngữ cảnh khi câu bị cắt đôi giữa hai chunk, giúp LLM nhận được thông tin mạch lạc và đầy đủ hơn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Technical Markdown Notes / Lab Materials

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain này vì các tài liệu hướng dẫn thực hành và ghi chú bài giảng chứa cấu trúc thông tin rất rõ ràng (sử dụng tiêu đề Markdown, danh sách, khối code). Việc ứng dụng RAG vào domain này giúp học viên nhanh chóng truy vấn kiến thức, tìm kiếm hướng dẫn thiết lập môi trường và các lệnh code mẫu mà không cần đọc lại toàn bộ tài liệu dài.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Day1.md | data/data_new/Day1.md | 8563 | {"source": "data/data_new/Day1.md", "extension": ".md"} |
| 2 | day2.md | data/data_new/day2.md | 6319 | {"source": "data/data_new/day2.md", "extension": ".md"} |
| 3 | day3.md | data/data_new/day3.md | 3915 | {"source": "data/data_new/day3.md", "extension": ".md"} |
| 4 | Day4.md | data/data_new/Day4.md | 7346 | {"source": "data/data_new/Day4.md", "extension": ".md"} |
| 5 | Day5.md | data/data_new/Day5.md | 2913 | {"source": "data/data_new/Day5.md", "extension": ".md"} |
| 6 | Day6.md | data/data_new/Day6.md | 3229 | {"source": "data/data_new/Day6.md", "extension": ".md"} |
| 7 | day7.md | data/data_new/day7.md | 6628 | {"source": "data/data_new/day7.md", "extension": ".md"} |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | `"data/data_new/Day1.md"` | Xác định nguồn gốc tài liệu chứa thông tin, giúp hiển thị nguồn dẫn (citation) chính xác cho người dùng và lọc tài liệu theo từng chương trình/bài học cụ thể. |
| extension | string | `".md"` | Cho phép lọc và giới hạn định dạng tài liệu truy vấn (ví dụ chỉ tìm kiếm tài liệu hướng dẫn dạng markdown thay vì văn bản thô). |
| chunk_index | integer | `2` | Giúp xác định vị trí tương đối của chunk trong văn bản gốc, hỗ trợ hiển thị ngữ cảnh xung quanh (lấy các chunk lân cận trước và sau) để cải thiện chất lượng trả lời. |
| doc_id | string | `"Day1"` | Giúp quản lý vòng đời tài liệu trong Vector Store, cho phép dễ dàng xóa hoặc cập nhật toàn bộ các chunk thuộc về cùng một tài liệu gốc khi tài liệu đó được sửa đổi. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| day7.md | FixedSizeChunker (`fixed_size`) | 17 | 480 | Không (cắt ngang câu và tiêu đề) |
| day7.md | SentenceChunker (`by_sentences`) | 34 | 224 | Trung bình (giữ nguyên câu nhưng phá vỡ cấu trúc danh sách) |
| day7.md | RecursiveChunker (`recursive`) | 20 | 380 | Tốt (giữ nguyên cấu trúc phân đoạn của Markdown) |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> `RecursiveChunker` hoạt động bằng cách chia nhỏ văn bản dựa trên một danh sách các dấu phân tách có thứ tự ưu tiên giảm dần (mặc định là `["\n\n", "\n", ". ", " ", ""]`). Đầu tiên, bộ chia thử phân tách văn bản bằng dấu phân tách có mức ưu tiên cao nhất (ví dụ: hai dòng xuống dòng `\n\n` tương ứng với ranh giới đoạn văn). Nếu bất kỳ đoạn phân tách nào có độ dài vượt quá `chunk_size` đã thiết lập, bộ chia sẽ thực hiện đệ quy trên đoạn đó bằng dấu phân tách tiếp theo (như xuống dòng đơn `\n` hoặc khoảng trắng `" "`). Quy trình này lặp lại cho đến khi mọi phân mảnh đều có kích thước nằm trong giới hạn cho phép, đảm bảo văn bản được chia tách tại các ranh giới tự nhiên nhất có thể.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tài liệu Markdown của nhóm có cấu trúc phân đoạn rõ ràng bằng tiêu đề (`##`), các đoạn văn và danh sách liệt kê. Sử dụng `RecursiveChunker` giúp giữ nguyên các khối thông tin logic đi liền với nhau (như một đoạn văn hoặc một khối mã lệnh) trong cùng một chunk. Điều này tối ưu hóa khả năng truy xuất thông tin có ngữ cảnh toàn vẹn và mạch lạc cho RAG hơn hẳn so với việc cắt cố định ký tự.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| day7.md | best baseline (SentenceChunker) | 34 | 224 | Trung bình (thông tin bị vụn vặt) |
| day7.md | **của tôi (RecursiveChunker)** | 20 | 380 | Rất tốt (ngữ cảnh đầy đủ và rõ ràng) |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tống Anh Huy | RecursiveChunker | 8.5/10 | Giữ được cấu trúc Markdown tự nhiên, ngữ cảnh trọn vẹn. | Đòi hỏi tính toán đệ quy phức tạp hơn, độ dài chunk không đều. |
| Trần Duy Khánh | RecursiveChunker | 8.5/10 | Tốc độ xử lý nhanh, kích thước chunk đồng đều. | Hay làm đứt gãy thông tin giữa chừng, ảnh hưởng xấu tới câu trả lời của Agent. |
| Mai Đức Vinh | SentenceChunker | 8/10 | Bảo toàn được ý nghĩa của từng câu đơn lẻ. | Mất liên kết giữa các câu trong cùng một phân đoạn lớn (như danh sách). |
| Nguyễn Đăng Khương | FixedSizeChunker | 7/10 | Tốc độ xử lý nhanh, kích thước chunk đồng đều. | Hay làm đứt gãy thông tin giữa chừng, ảnh hưởng xấu tới câu trả lời của Agent. |
| Nguyễn Mạnh Hiếu | FixedSizeChunker | 7/10 | Tốc độ xử lý nhanh, kích thước chunk đồng đều. | Hay làm đứt gãy thông tin giữa chừng, ảnh hưởng xấu tới câu trả lời của Agent. |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> RecursiveChunker là chiến lược tốt nhất cho domain tài liệu kỹ thuật Markdown. Nó đảm bảo các khối mã lệnh, danh sách liệt kê và các đoạn giải thích đi liền không bị cắt đôi một cách ngẫu nhiên, giúp Vector Store truy xuất được những khối thông tin có tính mạch lạc ngữ nghĩa cao nhất.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng biểu thức chính quy (regular expression) kết hợp lookbehind `(?<=\. |\! |\? |\.\n)` để phát hiện ranh giới câu mà không làm mất đi dấu kết thúc câu (`.`, `!`, `?`). Sau khi làm sạch khoảng trắng dư thừa, các câu đơn được nhóm lại với nhau theo giới hạn `max_sentences_per_chunk` và nối lại bằng dấu cách để tạo thành chunk hoàn chỉnh.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Triển khai thuật toán đệ quy trong phương thức `_split`. Nếu đoạn văn bản hiện tại nhỏ hơn `chunk_size`, nó đóng vai trò là base case và được trả về trực tiếp. Nếu lớn hơn, bộ chia sẽ duyệt qua danh sách separators. Khi tìm thấy dấu phân tách phù hợp, văn bản được split và mỗi phần con sẽ được kiểm tra kích thước: nếu quá khổ, nó sẽ được gửi vào một lời gọi đệ quy tiếp theo với các dấu phân tách còn lại trong danh sách; nếu nhỏ hơn hoặc bằng `chunk_size`, nó được giữ lại làm kết quả. Trường hợp hết dấu phân tách hoặc gặp `""`, bộ chia sẽ cắt văn bản theo các khối ký tự có kích thước `chunk_size`.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Lưu trữ tài liệu dưới dạng danh sách các dictionary (in-memory) có chứa ID, nội dung văn bản, embedding vector và metadata. Khi thực hiện tìm kiếm ngữ nghĩa (`search`), truy vấn đầu vào được chuyển thành vector thông qua hàm embedding, sau đó tính toán tích vô hướng (dot product) giữa vector truy vấn với vector của từng chunk đã lưu để xếp hạng độ tương đồng, trả về `top_k` chunk có điểm số cao nhất.

**`search_with_filter` + `delete_document`** — approach:
> Thực hiện lọc tài liệu bằng metadata trước (pre-filtering) bằng cách duyệt qua in-memory store và đối chiếu các cặp key-value trong bộ lọc `metadata_filter` với metadata của từng chunk, sau đó mới thực hiện tìm kiếm tương đồng trên các chunk đã vượt qua bộ lọc. Việc xóa tài liệu (`delete_document`) được thực hiện bằng cách lọc và giữ lại những chunk có `metadata['doc_id']` khác với `doc_id` cần xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> Đầu tiên truy xuất các chunk thông tin liên quan nhất từ `EmbeddingStore` thông qua câu hỏi của người dùng. Sau đó, nối nội dung của các chunk này lại làm ngữ cảnh nguồn (`context`) và đưa vào một prompt template được thiết kế sẵn. Cuối cùng, gửi prompt này tới hàm LLM (`llm_fn`) để sinh ra câu trả lời có tính căn cứ khoa học và tránh hiện tượng ảo giác.

### Test Results

```
================================================= 42 passed in 0.34s =================================================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Học viên cần cài đặt thư viện python-dotenv để nạp các biến môi trường. | Hãy sử dụng pip để cài đặt thư viện python-dotenv giúp quản lý cấu hình hệ thống. | high | 0.88 | Đúng |
| 2 | Để xóa tài liệu khỏi kho lưu trữ vector, chúng ta dùng phương thức delete_document. | Phương thức delete_document giúp loại bỏ toàn bộ các chunk của tài liệu dựa trên doc_id. | high | 0.85 | Đúng |
| 3 | Mô hình ngôn ngữ lớn hoạt động tốt nhất khi được cung cấp ngữ cảnh rõ ràng. | Để đạt kết quả tốt nhất, hãy cung cấp các thông tin ngữ cảnh đầy đủ cho LLM. | high | 0.89 | Đúng |
| 4 | Tôi thích ăn bánh mì kẹp thịt bò vào buổi sáng. | Kho lưu trữ vector sử dụng tích vô hướng để tính toán độ tương đồng. | low | 0.12 | Đúng |
| 5 | Hệ thống RAG truy xuất thông tin từ tài liệu gốc. | Không có thông tin nào được truy xuất từ tài liệu này cả. | low | 0.35 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là các câu có cấu trúc từ ngữ tương tự nhưng mang ý nghĩa đối lập (như Pair 5) vẫn có điểm số tương đồng cao hơn các câu hoàn toàn khác chủ đề (như Pair 4). Điều này cho thấy các mô hình embedding biểu diễn nghĩa bằng cách ánh xạ các từ vào không gian ngữ nghĩa liên tục; các từ xuất hiện trong cùng ngữ cảnh (như 'tài liệu', 'truy xuất') sẽ kéo các vector lại gần nhau, chứng minh embedding nắm bắt tốt chủ đề chung nhưng đôi khi gặp khó khăn với các tiểu tiết logic như phủ định.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Làm thế nào để thiết lập biến môi trường GEMINI_API_KEY? | Trên Windows dùng lệnh `$env:GEMINI_API_KEY="..."`, trên macOS/Linux dùng lệnh `export GEMINI_API_KEY="..."`. |
| 2 | ReAct Agent hoạt động theo chu trình nào? | ReAct Agent hoạt động theo chu trình lặp `Thought → Action → Observation`. |
| 3 | Các thấu kính quét cơ hội AI trong doanh nghiệp là gì? | Các thấu kính bao gồm: Lặp lại (Repetitive), Tốn thời gian (Time-consuming), AI-upgrade, và Stakeholder Pain. |
| 4 | Công thức tính số lượng chunk khi sử dụng Fixed Size Chunking là gì? | Công thức là `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`. |
| 5 | Làm thế nào để chạy demo Vinpearl ReAct Agent với mô hình cục bộ? | Đặt file GGUF vào thư mục `models/`, cập nhật cấu hình `.env` (`DEFAULT_PROVIDER=local` và `LOCAL_MODEL_PATH`), và chạy lệnh `python run_vinpearl_agent.py`. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Làm thế nào để thiết lập biến môi trường GEMINI_API_KEY? | Khai báo API key trong terminal: Windows dùng `$env:GEMINI_API_KEY`, macOS/Linux dùng `export GEMINI_API_KEY`... | 0.92 | Yes | Để thiết lập GEMINI_API_KEY: trên Windows chạy `$env:GEMINI_API_KEY="khóa_của_bạn"`, còn macOS/Linux chạy `export GEMINI_API_KEY="khóa_của_bạn"`. |
| 2 | ReAct Agent hoạt động theo chu trình nào? | Cài đặt chu trình Thought -> Action -> Observation trong file src/agent/agent.py... | 0.89 | Yes | ReAct Agent hoạt động theo chu trình tuần hoàn Thought -> Action -> Observation để đưa ra suy luận và thực thi công cụ phù hợp. |
| 3 | Các thấu kính quét cơ hội AI trong doanh nghiệp là gì? | Bảng quét cơ hội (SCAN)... thấu kính áp dụng: Lặp lại, Tốn thời gian, AI-upgrade, Stakeholder Pain... | 0.90 | Yes | Các thấu kính để quét cơ hội AI bao gồm: Lặp lại (Repetitive), Tốn thời gian (Time-consuming), AI-upgrade và Stakeholder Pain. |
| 4 | Công thức tính số lượng chunk khi sử dụng Fixed Size Chunking là gì? | Công thức: num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))... | 0.95 | Yes | Công thức tính số lượng chunk cho tài liệu là num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap)). |
| 5 | Làm thế nào để chạy demo Vinpearl ReAct Agent với mô hình cục bộ? | Tạo thư mục models/ đặt file GGUF vào... cập nhật .env... chạy python run_vinpearl_agent.py... | 0.91 | Yes | Để chạy demo, tải file mô hình Phi-3 instruct GGUF đặt vào thư mục models/, đặt `DEFAULT_PROVIDER=local` trong file `.env`, rồi thực thi `python run_vinpearl_agent.py`. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được từ thành viên trong nhóm cách thiết lập metadata phân cấp để tổ chức các bài học theo thứ tự tăng dần về độ khó. Điều này giúp hệ thống RAG không chỉ tìm kiếm theo ngữ nghĩa mà còn có thể lọc chính xác tài liệu phù hợp với trình độ của người truy vấn.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Qua phần demo của nhóm khác, tôi ấn tượng với cách họ xử lý các tài liệu chứa hình ảnh bằng cách trích xuất text mô tả hình ảnh tự động và chèn vào làm chú thích ngữ cảnh trong Markdown. Nhờ vậy, RAG vẫn có thể tìm kiếm được thông tin mô tả trực quan.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Nếu làm lại, tôi sẽ bổ sung thêm bước chuẩn hóa văn bản trước khi chunking (như loại bỏ các ký tự thừa, chuẩn hóa định dạng danh sách) và tối ưu hóa thêm ranh giới giữa các tiêu đề lớn để đảm bảo khi chia cắt tài liệu, tiêu đề luôn được đính kèm vào đầu của mỗi chunk tương ứng, giúp bảo toàn context tốt nhất.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 9 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 9 / 10 |
| Similarity predictions | Cá nhân | 3 / 5 |
| Results | Cá nhân | 9 / 10 |
| Retrieval Quality	Nhóm	7 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **90 / 100** |
