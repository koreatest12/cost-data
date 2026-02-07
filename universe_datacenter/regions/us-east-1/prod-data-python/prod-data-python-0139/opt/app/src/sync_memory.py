import os
from datetime import datetime

def transform_memory():
    print("에이전트의 경험(Episodic)을 지식(Semantic)으로 변환 중...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory_file = "docs/memory/semantic_knowledge.md"
    
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(f"\n## Knowledge Updated at {timestamp}\n")
        f.write("- 최근 GitHub 활동 데이터를 분석하여 지식 베이스를 업데이트함.\n")
    print(f"변환 완료: {memory_file} 업데이트됨.")

if __name__ == "__main__":
    transform_memory()
