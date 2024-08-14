def admit_students(university, major, admission_score, enrollments, teachers,
                   candidates_scores):
    candidates = {name: score for name, score in candidates_scores.items()}
    qualified_candidates = [
        name for name, score in candidates.items() if score >= admission_score
    ]
    qualified_count = len(qualified_candidates)

    admission = qualified_candidates[:enrollments]

    print(f"大学名称: {university}")
    print(f"专业: {major}")
    print(f"招生分数线: {admission_score}")
    print(f"招生人数: {enrollments}")
    print(f"招生老师名单: {', '.join(teachers)}")
    print(f"报考考生及其高考成绩: {candidates}")
    print(f"报考人数: {len(candidates)}")
    print(f"达线人数: {qualified_count}")
    print(f"录取名单: {admission}")
    print(f"录取人数: {len(admission)}")


university = '西北大学'
major = '计算机科学'
teachers = ["张老师", "王老师", "李老师"]
candidates_scores = {'张旭': 540, '李阳': 575, '王强': 583, '徐增': 569, '齐飞': 557}

admit_students(university, major, 550, 2, teachers, candidates_scores)
