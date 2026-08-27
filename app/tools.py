def analyze_gap(required_skills: list[str], my_skills: list[str]) -> dict:
    result = {"matched":[], "missing": []}
    for skill in list(map(str.lower,required_skills)):
        if skill in list(map(str.lower, my_skills)):
            result["matched"].append(skill)
        else:
            result["missing"].append(skill)
    return result

def main():
    required_skills = ["Python", "LangGraph", "Docker"]
    my_skills = ["python", "Docker"]

    # Fixed the keyword argument name to match your list variable
    test = analyze_gap(required_skills=required_skills, my_skills=my_skills)
    print(test)

# Fixed: Removed the quotes around __name__
if __name__ == "__main__":
    main()