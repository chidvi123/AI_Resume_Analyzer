"""
Course recommendations per job role.
Each list contains (course_title, url) tuples.
"""

# ─── Data Science / ML / AI ───────────────────────────────────────────────────
ds_course = [
    ['Machine Learning Crash Course by Google [Free]', 'https://developers.google.com/machine-learning/crash-course'],
    ['Machine Learning A-Z by Udemy', 'https://www.udemy.com/course/machinelearning/'],
    ['Machine Learning by Andrew NG', 'https://www.coursera.org/learn/machine-learning'],
    ['Data Scientist Master Program of Simplilearn (IBM)', 'https://www.simplilearn.com/big-data-and-analytics/senior-data-scientist-masters-program-training'],
    ['Data Scientist with Python', 'https://www.datacamp.com/tracks/data-scientist-with-python'],
    ['Programming for Data Science with Python', 'https://www.udacity.com/course/programming-for-data-science-nanodegree--nd104'],
    ['Intro to Machine Learning with TensorFlow', 'https://www.udacity.com/course/intro-to-machine-learning-with-tensorflow-nanodegree--nd230'],
    ['Applied Data Science with Python Specialization', 'https://www.coursera.org/specializations/data-science-python'],
]

# ─── Web Development ─────────────────────────────────────────────────────────
web_course = [
    ['Django Crash course [Free]', 'https://youtu.be/e1IyzVyrLSU'],
    ['Python and Django Full Stack Web Developer Bootcamp', 'https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp'],
    ['React Crash Course [Free]', 'https://youtu.be/Dorf8i6lCuk'],
    ['Full Stack Web Developer - MEAN Stack', 'https://www.simplilearn.com/full-stack-web-developer-mean-stack-certification-training'],
    ['Node.js and Express.js [Free]', 'https://youtu.be/Oe421EPjeBE'],
    ['Flask: Develop Web Applications in Python', 'https://www.educative.io/courses/flask-develop-web-applications-in-python'],
    ['Full Stack Web Developer by Udacity', 'https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044'],
    ['The Web Developer Bootcamp by Udemy', 'https://www.udemy.com/course/the-web-developer-bootcamp/'],
]

# ─── Android ─────────────────────────────────────────────────────────────────
android_course = [
    ['Android Development for Beginners [Free]', 'https://youtu.be/fis26HvvDII'],
    ['Android App Development Specialization', 'https://www.coursera.org/specializations/android-app-development'],
    ['Associate Android Developer Certification', 'https://grow.google/androiddev/#?modal_active=none'],
    ['Become an Android Kotlin Developer by Udacity', 'https://www.udacity.com/course/android-kotlin-developer-nanodegree--nd940'],
    ['The Complete Android Developer Course', 'https://www.udemy.com/course/complete-android-n-developer-course/'],
    ['Flutter & Dart - The Complete Flutter App Development Course', 'https://www.udemy.com/course/flutter-dart-the-complete-flutter-app-development-course/'],
]

# ─── iOS ─────────────────────────────────────────────────────────────────────
ios_course = [
    ['iOS & Swift - The Complete iOS App Development Bootcamp', 'https://www.udemy.com/course/ios-13-app-development-bootcamp/'],
    ['Become an iOS Developer', 'https://www.udacity.com/course/ios-developer-nanodegree--nd003'],
    ['iOS App Development with Swift Specialization', 'https://www.coursera.org/specializations/app-development'],
    ['Swift Tutorial - Full Course for Beginners [Free]', 'https://youtu.be/comQ1-x2a1Q'],
    ['Learn Swift Fast - [Free]', 'https://youtu.be/FcsY1YPBwzQ'],
]

# ─── UI/UX ────────────────────────────────────────────────────────────────────
uiux_course = [
    ['Google UX Design Professional Certificate', 'https://www.coursera.org/professional-certificates/google-ux-design'],
    ['UI / UX Design Specialization', 'https://www.coursera.org/specializations/ui-ux-design'],
    ['The Complete App Design Course - UX, UI and Design Thinking', 'https://www.udemy.com/course/the-complete-app-design-course-ux-and-ui-design/'],
    ['Become a UX Designer by Udacity', 'https://www.udacity.com/course/ux-designer-nanodegree--nd578'],
    ['Adobe XD Tutorial: User Experience Design Course [Free]', 'https://youtu.be/68w2VwalD5w'],
]

# ─── DevOps ───────────────────────────────────────────────────────────────────
devops_course = [
    ['Docker and Kubernetes: The Complete Guide', 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/'],
    ['DevOps Beginners to Advanced with Projects [Udemy]', 'https://www.udemy.com/course/devsecops/'],
    ['DevOps Engineering on AWS', 'https://www.coursera.org/learn/aws-cloud-technical-essentials'],
    ['CI/CD Pipelines with Jenkins [Free]', 'https://youtu.be/FX322RVNGj4'],
    ['Terraform for Beginners [Free]', 'https://youtu.be/SLB_c_ayRMo'],
    ['Linux Command Line Basics [Free]', 'https://youtu.be/ZtqBQ68cfJc'],
    ['Google SRE / DevOps Certificate', 'https://www.coursera.org/professional-certificates/sre-devops-engineer-google-cloud'],
]

# ─── QA / Testing ─────────────────────────────────────────────────────────────
qa_course = [
    ['Selenium WebDriver with Python [Udemy]', 'https://www.udemy.com/course/selenium-real-time-exams-interview-questions/'],
    ['Software Testing & Automation Specialization', 'https://www.coursera.org/specializations/software-testing-automation'],
    ['ISTQB Foundation Level Certification Prep', 'https://www.udemy.com/course/istqb-certified-tester-foundation-level/'],
    ['API Testing with Postman [Free]', 'https://youtu.be/VywxIQ2ZXw4'],
    ['Pytest for Beginners [Free]', 'https://youtu.be/byaxg00Gf9I'],
    ['Test Automation University [Free]', 'https://testautomationu.applitools.com/'],
]

# ─── Software Engineering ─────────────────────────────────────────────────────
software_course = [
    ['Data Structures & Algorithms — Full Course [Free]', 'https://youtu.be/pkYVOmU3MgA'],
    ['System Design for Beginners [Free]', 'https://youtu.be/MbjObHmDbZo'],
    ['Object-Oriented Programming in Python [Free]', 'https://youtu.be/Ej_02ICOIgs'],
    ['Clean Code by Robert C. Martin [Summary]', 'https://youtu.be/7EmboKQH8lM'],
    ['LeetCode 75 — Top Interview Questions', 'https://leetcode.com/studyplan/leetcode-75/'],
    ['Software Engineering Essentials [IBM on Coursera]', 'https://www.coursera.org/learn/software-engineering-essentials'],
]

# ─── Mobile App Development ───────────────────────────────────────────────────
mobile_course = [
    ['Flutter & Dart - Complete Flutter Development Course', 'https://www.udemy.com/course/flutter-dart-the-complete-flutter-app-development-course/'],
    ['React Native - The Practical Guide', 'https://www.udemy.com/course/react-native-the-practical-guide/'],
    ['Android Kotlin Development Masterclass', 'https://www.udemy.com/course/android-oreo-kotlin-app-masterclass/'],
    ['Flutter Full Course for Beginners [Free]', 'https://youtu.be/VPvVD8t02U8'],
    ['Cross Platform Mobile Dev with Flutter [Coursera]', 'https://www.coursera.org/learn/flutter-development'],
    ['Firebase for Flutter [Free]', 'https://youtu.be/sfA3NWDBPZ4'],
]

# ─── Data Analysis ────────────────────────────────────────────────────────────
analyst_course = [
    ['Google Data Analytics Professional Certificate', 'https://www.coursera.org/professional-certificates/google-data-analytics'],
    ['Data Analysis with Python [freeCodeCamp, Free]', 'https://youtu.be/r-uOLxNrNk8'],
    ['SQL for Data Analysis [Mode Analytics, Free]', 'https://mode.com/sql-tutorial/'],
    ['Power BI Full Course [Free]', 'https://youtu.be/AGrl-H87pRU'],
    ['Tableau for Beginners', 'https://www.udemy.com/course/tableau10/'],
    ['Excel Skills for Data Analytics [Coursera]', 'https://www.coursera.org/learn/excel-data-analysis'],
]

# ─── Resume & Interview Videos ────────────────────────────────────────────────
resume_videos = [
    'https://youtu.be/Tt08KmFfIYQ', 'https://youtu.be/y8YH0Qbu5h4',
    'https://youtu.be/u75hUSShvnc', 'https://youtu.be/BYUy1yvjHxE',
    'https://youtu.be/KFaugkGVeNQ', 'https://youtu.be/3agP4x8LYFM',
    'https://youtu.be/GyjzOKdaioU', 'https://youtu.be/17YZBH_qtmg',
    'https://youtu.be/aKjsy-b00QM', 'https://youtu.be/ciIkiWwZnlc'
]

interview_videos = [
    'https://youtu.be/HG68Ymazo18', 'https://youtu.be/BOvAAoxM4vg',
    'https://youtu.be/KukmClH1KoA', 'https://youtu.be/7_aAicmPB3A',
    'https://youtu.be/1mHjMNZZvFo', 'https://youtu.be/WfdtKbAJOmE',
    'https://youtu.be/IBjM-F56qS0', 'https://youtu.be/4tYoVx0QoN0',
    'https://youtu.be/Ge0Udbws1kc', 'https://youtu.be/thkuu_FWFD8',
    'https://youtu.be/e0E6-dRPcJA',
]


# ─── Main function ────────────────────────────────────────────────────────────
def get_recommended_courses(target_role: str) -> list:
    role = target_role.lower()

    if "data_scientist" in role or "ml" in role or ("data" in role and "scientist" in role):
        return ds_course
    elif "machine_learning" in role or "machine learning" in role:
        return ds_course
    elif "data_analyst" in role or ("data" in role and "analyst" in role):
        return analyst_course
    elif "devops" in role:
        return devops_course
    elif "qa" in role or "quality" in role or "test" in role:
        return qa_course
    elif "mobile" in role:
        return mobile_course
    elif "android" in role:
        return android_course
    elif "ios" in role or "swift" in role:
        return ios_course
    elif "software_engineer" in role or ("software" in role and "engineer" in role):
        return software_course
    elif "fullstack" in role or "full_stack" in role or "full stack" in role:
        return web_course
    elif "frontend" in role or "front_end" in role or "front end" in role:
        return web_course
    elif "backend" in role or "back_end" in role or "back end" in role:
        return web_course
    elif "web" in role:
        return web_course
    elif "ui" in role or "ux" in role:
        return uiux_course

    return []