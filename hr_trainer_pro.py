import re, random, json
from textblob import TextBlob
from datetime import datetime

class ProHRTrainer:
    def __init__(self):
        self.questions_db = {
            'introduction': [
                "Tell me about yourself in 2 minutes.",
                "What are your top 3 strengths with examples?",
                "Why should we hire you over other candidates?",
                "Walk me through your resume."
            ],
            'behavioral': [
                "Tell me about a time you failed and what you learned.",
                "Describe a time you showed leadership without authority.",
                "Tell me about a conflict with a teammate and how you resolved it.",
                "Describe a time you had to meet a tight deadline.",
                "Tell me about a time you took initiative."
            ],
            'situational': [
                "Your manager gives you wrong feedback, what will you do?",
                "You have 2 deadlines same day, how will you prioritize?",
                "Your team member is not contributing, how will you handle?",
                "If you find a bug in production at 11pm, what will you do?"
            ],
            'company_fit': [
                "Why do you want to join Google/Amazon/Microsoft?",
                "What do you know about our culture?",
                "Where do you see yourself in 5 years?",
                "What are your salary expectations and why?"
            ],
            'technical_hr': [
                "Explain your final year project to a non-technical HR.",
                "What is the biggest challenge in AI/Data Science?",
                "How do you stay updated with latest tech?"
            ]
        }

        self.company_db = {
            'Google': ['Googliness','Innovation','User Focus','Scalability','Tell me about ambiguous problem'],
            'Amazon': ['Leadership Principles','Customer Obsession','Ownership','Bias for Action','STAR is mandatory'],
            'TCS': ['Learning agility','Team collaboration','Client focus'],
            'Infosys': ['Power of flexibility','Be humble']
        }

        self.positive_words = ['achieved','learned','successful','improved','led','created','collaborated','solved','delivered','impact','growth','initiative','ownership']
        self.negative_words = ['failed','blamed','hate','angry','quit','problem without solution','i dont know']
        self.star_keywords = {
            'situation': ['situation','context','background','faced','challenge','project','team'],
            'task': ['task','responsibility','goal','objective','assigned','role'],
            'action': ['action','i did','i took','implemented','organized','created','developed','led','initiated'],
            'result': ['result','outcome','achieved','improved','increased','reduced','success','impact','learned']
        }

    def analyze_response(self, question, response, target_company="Google"):
        text = response.lower()
        words = response.split()
        blob = TextBlob(response)

        # 1. Length & Structure
        word_count = len(words)
        sentence_count = len(re.findall(r'[.!?]', response))

        # 2. STAR Score
        star_scores = {}
        for part, keywords in self.star_keywords.items():
            star_scores[part] = any(k in text for k in keywords)
        star_score = sum(star_scores.values()) / 4 * 100

        # 3. Sentiment & Confidence Analysis
        sentiment = blob.sentiment.polarity # -1 to 1
        confidence_score = 0
        if "i am confident" in text or "i believe" in text: confidence_score += 10
        if len(re.findall(r'\b(i|me|my)\b', text)) > 10: confidence_score += 10 # ownership
        if "um" in text or "uh" in text or "like" in text: confidence_score -= 15
        if sentiment > 0.2: confidence_score += 20
        if word_count > 60 and sentence_count >= 3: confidence_score += 20

        confidence_score = max(0, min(100, 60 + confidence_score))

        # 4. Behavioral Scoring
        positive_count = sum(1 for w in self.positive_words if w in text)
        negative_count = sum(1 for w in self.negative_words if w in text)
        behavioral_score = min(100, 40 + positive_count*8 - negative_count*15 + star_score*0.4)

        # 5. Company Fit
        company_tips = self.company_db.get(target_company, [])
        company_fit = 70
        if target_company == "Amazon" and star_score < 75:
            company_fit -= 20 # Amazon loves STAR

        # 6. Filler words detection
        fillers = len(re.findall(r'\b(um|uh|like|you know|actually|basically)\b', text, re.I))

        total_score = round((star_score*0.35 + behavioral_score*0.30 + confidence_score*0.20 + company_fit*0.15), 1)

        # Feedback Generation - Personalized
        feedback = []
        if not star_scores['situation']: feedback.append("❌ Missing Situation: Start with 'In my previous project...'")
        else: feedback.append("✅ Good Situation context")
        if not star_scores['task']: feedback.append("❌ Missing Task: Clearly say 'My responsibility was to...'")
        else: feedback.append("✅ Task defined well")
        if not star_scores['action']: feedback.append("❌ Missing Action: Use 'I implemented / I led' - show ownership")
        else: feedback.append("✅ Strong Action verbs")
        if not star_scores['result']: feedback.append("❌ Missing Result: Always end with numbers - 'Result: 30% improvement'")
        else: feedback.append("✅ Result quantified")

        if word_count < 40: feedback.append("⚠️ Too short (HR expects 60-120 words). Add example.")
        elif word_count > 180: feedback.append("⚠️ Too long - Keep it under 2 mins (120 words)")
        else: feedback.append("✅ Ideal length for HR")

        if fillers > 2: feedback.append(f"⚠️ {fillers} filler words (um, like) detected - Practice to sound confident")
        if sentiment < 0: feedback.append("⚠️ Negative sentiment - Use positive learning tone")
        if positive_count < 2: feedback.append("💡 Add power verbs: Achieved, Led, Delivered, Improved")

        tips = [
            f"For {target_company}: {random.choice(company_tips) if company_tips else 'Be concise and structured'}",
            "Use numbers: 'Improved by 25%', 'Led team of 4'",
            "End with learning: 'This taught me importance of communication'"
        ]

        return {
            'total': total_score,
            'star_score': round(star_score,1),
            'behavioral': round(behavioral_score,1),
            'confidence': round(confidence_score,1),
            'sentiment': round(sentiment,2),
            'word_count': word_count,
            'fillers': fillers,
            'star_breakdown': star_scores,
            'feedback': feedback,
            'tips': tips,
            'grade': "A+ Excellent" if total_score>=85 else "A Good" if total_score>=70 else "B Needs Practice" if total_score>=55 else "C Poor"
        }

    def get_random_questions(self, company="Google", count=5):
        all_q = []
        for cat, qs in self.questions_db.items():
            for q in qs:
                all_q.append({'q': q, 'cat': cat})
        # Add company specific
        if company in self.company_db:
            all_q.append({'q': f"Why {company}? What do you know about {company}?", 'cat': 'company_fit'})
        return random.sample(all_q, min(count, len(all_q)))