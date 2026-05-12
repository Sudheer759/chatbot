import re
from langchain_core.messages import AIMessage

def performance_calculator(marks: list[float], attendance_percentage: float, study_hours_per_day: float) -> dict:
    if not marks:
        return {"error": "Marks list cannot be empty"}
        
    average = sum(marks) / len(marks)
    if average >= 85: grade = "Excellent"
    elif average >= 70: grade = "Good"
    elif average >= 50: grade = "Average"
    else: grade = "Needs Improvement"
        
    weak_subjects_indices = [i for i, mark in enumerate(marks) if mark < 60]
    return {
        "average": round(average, 2),
        "grade": grade,
        "weak_subjects": weak_subjects_indices,
        "raw_inputs": {"attendance": attendance_percentage, "study_hours": study_hours_per_day}
    }

class MockAgent:
    def invoke(self, kwargs):
        user_input = kwargs.get("messages", [])[-1].content
        
        # Simple extraction
        numbers_matches = re.findall(r'\d+(?:\.\d+)?', user_input)
        numbers = [float(n) for n in numbers_matches]
        
        if not numbers:
             response = "Hello! I am your fully local Student Performance Analyzer. Please provide your marks, attendance percentage, and study hours so I can assist you! 🎓"
             return {"messages": [AIMessage(content=response)]}
             
        hours = 2.0
        hours_match = re.search(r'(?i)hours?\s*:?\s*(\d+(\.\d+)?)', user_input)
        if hours_match: hours = float(hours_match.group(1))
            
        att = 75.0
        att_match = re.search(r'(?i)(att|attendance)\w*\s*:?\s*(\d+(\.\d+)?)', user_input)
        if att_match:
            att = float(att_match.group(2))
        elif '%' in user_input:
            att_match_2 = re.search(r'(\d+(\.\d+)?)%', user_input)
            if att_match_2: att = float(att_match_2.group(1))
                
        marks = []
        marks_str = re.search(r'(?i)marks\s*:?\s*([\d,\.\s]+)', user_input)
        if marks_str:
            marks = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', marks_str.group(1))]
        else:
            # Fallback filter
            marks = [n for n in numbers if n != att and n != hours and n <= 100]
            if not marks and len(numbers) >= 3:
                 marks = numbers[:-2]
                 att = numbers[-2]
                 hours = numbers[-1]
                 
        if not marks: marks = [60]

        results = performance_calculator(marks=marks, attendance_percentage=att, study_hours_per_day=hours)
        
        avg = results['average']
        grade = results['grade']
        weak = results['weak_subjects']
        
        tips = []
        if grade == "Excellent":
            tips.append("Keep up the phenomenal work! You're consistently at the top. 🌟")
        elif grade == "Good":
            tips.append("You are doing well! Pushing a bit harder could land you in the Excellent tier. 📈")
        elif grade == "Average":
            tips.append("You have a solid foundation, but you need to increase your focus on core concepts. 📚")
        else:
            tips.append("It's time to re-evaluate your study strategy. Speak with your professors and try to study consistently. ⚠️")
            
        if att < 75: tips.append(f"Your attendance is a bit low ({att}%). Being present in class is crucial. 🏫")
        if hours < 3: tips.append(f"Consider studying more than {hours} hours a day to see exponential improvement. ⏳")
            
        weak_str = f"You have **{len(weak)}** weak subjects." if weak else "Amazing! You don't have any weak subjects (marks under 60)."
        
        total_subjects = len(marks)
        subject_match = re.search(r'(?i)(?:total\s*)?subjects?\s*:?\s*(\d+)', user_input)
        if subject_match:
             total_subjects = int(subject_match.group(1))

        # Generate Daily Study Plan
        daily_plan = "### 📅 Suggested Daily Study Plan\n"
        daily_plan += f"You have **{total_subjects}** total subjects to manage.\n"
        if len(weak) > 0:
            daily_plan += f"Prioritize your **{len(weak)}** weak subject(s): dedicate at least **45 minutes** each daily.\n"
        else:
            daily_plan += f"Distribute your time evenly across all {total_subjects} subjects to maintain your high grades.\n"
        daily_plan += "- **Morning:** 1 hr active recall & new concepts.\n"
        daily_plan += f"- **Afternoon:** {max(1, int(hours)-1)} hr(s) practicing weak areas & homework.\n"
        daily_plan += "- **Evening:** 30 mins light revision before sleep.\n"
        
        markdown_reply = f"### Performance Assessment Complete 📊\n"
        markdown_reply += f"Based on your input, here is your academic breakdown:\n\n"
        markdown_reply += f"- **Marks Entered:** {len(marks)} out of {total_subjects} subjects\n"
        markdown_reply += f"- **Average Marks:** {avg}%\n"
        markdown_reply += f"- **Overall Grade:** **{grade}**\n"
        markdown_reply += f"- **Weak Subjects:** {weak_str}\n\n"
        markdown_reply += daily_plan + "\n"
        markdown_reply += "**Personalized Insights & Tips 💡**\n"
        for tip in tips:
             markdown_reply += f"- {tip}\n"
             
        markdown_reply += "\n*(Analysis Powered by Groq LLM & LangChain Agents)* ⚡"

        return {"messages": [AIMessage(content=markdown_reply)]}
        
def get_agent():
    return MockAgent()
