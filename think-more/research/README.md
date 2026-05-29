# 📈 AI 에이전트 기술 동향 리서치 (Research)

이 디렉토리는 단순한 대화형 언어 모델(Chatbot)을 넘어 **자율적으로 문제를 해결하는 AI 에이전트(Agentic System)**의 기술적 발전 트렌드와 아키텍처를 연구하고 기록하는 스터디 보관소입니다.

에이전트의 구동 원리를 깊이 이해할수록, 에이전트의 한계(Hallucination, Loop 등)를 예방하고 더욱 복잡한 문제를 지시하는 능력을 기를 수 있습니다.

---

## 🔍 핵심 연구 키워드 (Key Keywords)

에이전트의 발전 과정을 추적하기 위해 눈여겨봐야 할 핵심 개념들입니다.

### 1. 🧠 기획 및 추론 (Planning & Reasoning)
* **ReAct (Reason + Act)**: 생각하고 행동하는 과정을 반복하며 문제를 해결하는 루프.
* **Chain of Thought (CoT)**: 단계적으로 추론하여 정답률을 높이는 기법.
* **Plan-and-Solve**: 전체 계획을 먼저 수립한 뒤, 세부 단계를 실행하는 에이전트 아키텍처.

### 2. 🗂️ 메모리 시스템 (Memory)
* **Short-term Memory**: 현재 대화 맥락 내의 정보 유지.
* **Long-term Memory (RAG / Vector DB)**: 이전 프로젝트나 영구적인 지식 데이터베이스에서 정보를 인출하여 활용하는 능력.

### 3. 🛠️ 도구 연동 (Tool Use / Function Calling)
* 에이전트가 스스로 판단하여 브라우징, 터미널 명령 실행, 파일 읽기/쓰기 등의 도구를 사용하는 메커니즘.

### 4. 👥 멀티 에이전트 시스템 (Multi-Agent System)
* 하나의 큰 작업을 여러 전문 에이전트(예: 기획자 에이전트, 개발자 에이전트, 검증자 에이전트)에게 나누어 맡겨 협업시키는 방식.

---

## 📚 스터디 노트 및 연구 리포트

*(학습 내용이나 기술 분석 리포트를 작성할 때마다 아래에 링크를 추가해 주세요)*

* [x] [Research 01] [LUI의 도래와 에이전트의 도구 사용 패러다임](01_agentic_interface_and_tools.md) (2026-05-22)
* [x] [Research 02] [멀티 디바이스 환경에서의 에이전트 지속성 메모리와 한계](02_cross_device_agent_and_memory.md) (2026-05-22)
* [x] [Research 03] [업계 구현 사례](03_industry_implementations.md)
* [x] [Research 04] [멀티 에이전트와 도메인 집중의 이점](multi_agent_benefits.md)
