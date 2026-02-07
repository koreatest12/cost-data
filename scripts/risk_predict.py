import sys, random
score = random.randint(10, 90)
level = "고위험" if score > 70 else "중위험" if score > 40 else "저위험"
print(f"재범 위험성: {score}/100 ({level})")
