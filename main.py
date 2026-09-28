import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar

# -----------------------------------
# 페이지 설정
# -----------------------------------

st.set_page_config(
    page_title="시험기간 공부 계획 재설계",
    page_icon="📚",
    layout="wide"
)

st.title("📚 시험기간 맞춤형 공부 계획")
st.write(
    "시험까지 남은 시간과 과목별 중요도, 목표를 바탕으로 "
    "공부 시간을 자동으로 배분합니다."
)

# -----------------------------------
# 함수
# -----------------------------------

def format_time(hours):
    """시간을 'X시간 Y분' 형태로 변환"""
    total_minutes = round(hours * 60)

    h = total_minutes // 60
    m = total_minutes % 60

    if h == 0:
        return f"{m}분"

    if m == 0:
        return f"{h}시간"

    return f"{h}시간 {m}분"


# -----------------------------------
# 기본 과목
# -----------------------------------

subjects = [
    "국어",
    "수학",
    "영어",
    "물리학",
    "생명과학",
    "화학"
]

# -----------------------------------
# 시험 정보
# -----------------------------------

st.header("1. 시험 정보")

col1, col2 = st.columns(2)

with col1:
    exam_date = st.date_input(
        "시험 날짜",
        value=date.today() + timedelta(days=7)
    )

with col2:
    daily_study_time = st.number_input(
        "하루에 공부할 수 있는 시간",
        min_value=0.5,
        max_value=24.0,
        value=5.0,
        step=0.5
    )

today = date.today()

days_left = (exam_date - today).days

if days_left < 0:
    st.error("시험 날짜는 오늘 이후로 설정해주세요.")
    st.stop()

# 오늘 포함
study_days = days_left + 1

total_study_time = study_days * daily_study_time

st.info(
    f"📅 시험일까지 **{days_left}일** 남았습니다.  \n"
    f"📚 공부할 수 있는 날: **{study_days}일**  \n"
    f"⏱️ 총 공부 가능 시간: **{format_time(total_study_time)}**"
)

# -----------------------------------
# 과목별 정보
# -----------------------------------

st.header("2. 과목별 중요도와 목표")

st.write(
    "각 과목의 중요도와 이번 시험에서 얼마나 점수를 올리고 싶은지를 설정하세요."
)

subject_info = {}

for subject in subjects:

    with st.expander(f"📖 {subject}", expanded=False):

        col1, col2 = st.columns(2)

        with col1:
            importance = st.slider(
                "과목 중요도",
                min_value=1,
                max_value=5,
                value=3,
                key=f"importance_{subject}"
            )

        with col2:
            goal = st.slider(
                "점수 향상 목표",
                min_value=1,
                max_value=5,
                value=3,
                key=f"goal_{subject}"
            )

        subject_info[subject] = {
            "importance": importance,
            "goal": goal
        }

# -----------------------------------
# 계획 생성
# -----------------------------------

st.header("3. 공부 계획 생성")

if st.button("📅 공부 계획 만들기", type="primary"):

    # -----------------------------------
    # 우선순위 계산
    # -----------------------------------

    for subject in subjects:

        importance = subject_info[subject]["importance"]
        goal = subject_info[subject]["goal"]

        priority = (
            importance * 0.6
            + goal * 0.4
        )

        subject_info[subject]["priority"] = priority

    # -----------------------------------
    # 전체 우선순위
    # -----------------------------------

    total_priority = sum(
        subject_info[subject]["priority"]
        for subject in subjects
    )

    # -----------------------------------
    # 과목별 총 공부시간
    # -----------------------------------

    for subject in subjects:

        priority = subject_info[subject]["priority"]

        study_time = (
            total_study_time
            * priority
            / total_priority
        )

        subject_info[subject]["study_time"] = study_time

    # -----------------------------------
    # 우선순위 정렬
    # -----------------------------------

    sorted_subjects = sorted(
        subjects,
        key=lambda x: subject_info[x]["priority"],
        reverse=True
    )

    # -----------------------------------
    # 분석 결과
    # -----------------------------------

    st.header("4. 과목별 분석")

    result_data = []

    for subject in sorted_subjects:

        result_data.append({
            "과목": subject,
            "중요도": subject_info[subject]["importance"],
            "목표": subject_info[subject]["goal"],
            "우선순위": round(
                subject_info[subject]["priority"],
                2
            ),
            "총 공부시간": format_time(
                subject_info[subject]["study_time"]
            )
        })

    df = pd.DataFrame(result_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------
    # 가장 우선순위 높은 과목
    # -----------------------------------

    first_subject = sorted_subjects[0]

    st.success(
        f"현재 조건에서 가장 높은 우선순위를 가진 과목은 "
        f"**{first_subject}**입니다."
    )

    # -----------------------------------
    # 하루 공부시간 계산
    # -----------------------------------

    daily_plan = {}

    for subject in sorted_subjects:

        priority = subject_info[subject]["priority"]

        daily_time = (
            daily_study_time
            * priority
            / total_priority
        )

        daily_plan[subject] = daily_time

    # -----------------------------------
    # 하루 공부 계획
    # -----------------------------------

    st.header("5. 하루 공부 계획")

    daily_data = []

    for subject in sorted_subjects:

        daily_data.append({
            "과목": subject,
            "하루 공부시간": format_time(
                daily_plan[subject]
            )
        })

    daily_df = pd.DataFrame(daily_data)

    st.dataframe(
        daily_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------
    # 달력
    # -----------------------------------

    st.header("6. 📅 시험 전 공부 달력")

    st.write(
        "날짜별로 어떤 과목을 얼마나 공부해야 하는지 확인할 수 있습니다."
    )

    # 날짜별 공부 계획 생성
    calendar_plan = {}

    for i in range(study_days):

        current_date = today + timedelta(days=i)

        day_plan = []

        for subject in sorted_subjects:

            study_time = daily_plan[subject]

            day_plan.append({
                "subject": subject,
                "time": study_time
            })

        calendar_plan[current_date] = day_plan

    # -----------------------------------
    # 월별 달력
    # -----------------------------------

    current_month = today.month
    current_year = today.year

    months_to_show = []

    temp_date = today

    while temp_date <= exam_date:

        month_key = (
            temp_date.year,
            temp_date.month
        )

        if month_key not in months_to_show:
            months_to_show.append(month_key)

        if temp_date.month == 12:
            temp_date = date(
                temp_date.year + 1,
                1,
                1
            )
        else:
            temp_date = date(
                temp_date.year,
                temp_date.month + 1,
                1
            )

    # -----------------------------------
    # 달력 출력
    # -----------------------------------

    for year, month in months_to_show:

        st.subheader(
            f"{year}년 {month}월"
        )

        cal = calendar.Calendar(
            firstweekday=6
        )

        weeks = cal.monthdayscalendar(
            year,
            month
        )

        # 요일
        weekday_cols = st.columns(7)

        weekdays = [
            "일",
            "월",
            "화",
            "수",
            "목",
            "금",
            "토"
        ]

        for col, weekday in zip(
            weekday_cols,
            weekdays
        ):
            col.markdown(
                f"**{weekday}**"
            )

        # 날짜
        for week in weeks:

            cols = st.columns(7)

            for col, day in zip(
                cols,
                week
            ):

                if day == 0:
                    continue

                current_date = date(
                    year,
                    month,
                    day
                )

                # 시험기간에 포함되지 않는 날짜
                if (
                    current_date < today
                    or current_date > exam_date
                ):
                    col.write(day)
                    continue

                # 날짜 표시
                if current_date == exam_date:

                    col.markdown(
                        f"### 🔴 {day}"
                    )
                    col.caption("시험")

                elif current_date == today:

                    col.markdown(
                        f"### 🟢 {day}"
                    )
                    col.caption("오늘")

                else:

                    col.markdown(
                        f"**{day}**"
                    )

                # 해당 날짜 공부계획
                day_plan = calendar_plan.get(
                    current_date,
                    []
                )

                for item in day_plan:

                    subject = item["subject"]
                    study_time = item["time"]

                    col.write(
                        f"📖 {subject}"
                    )

                    col.caption(
                        format_time(study_time)
                    )

    # -----------------------------------
    # 전체 계획
    # -----------------------------------

    st.header("7. 📋 날짜별 상세 계획")

    for i in range(study_days):

        current_date = today + timedelta(days=i)

        if current_date == exam_date:

            title = (
                f"🔴 {current_date.strftime('%m월 %d일')} "
                f"— 시험일"
            )

        elif current_date == today:

            title = (
                f"🟢 {current_date.strftime('%m월 %d일')} "
                f"— 오늘"
            )

        else:

            title = (
                f"📅 {current_date.strftime('%m월 %d일')}"
            )

        with st.expander(title):

            for subject in sorted_subjects:

                study_time = daily_plan[subject]

                st.write(
                    f"**{subject}** → "
                    f"{format_time(study_time)}"
                )
