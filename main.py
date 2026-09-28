import streamlit as st
import pandas as pd

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
# 기본 설정
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
# 시험 정보 입력
# -----------------------------------

st.header("1. 시험 정보")

col1, col2 = st.columns(2)

with col1:
    days_left = st.number_input(
        "시험까지 남은 날짜",
        min_value=1,
        max_value=100,
        value=7
    )

with col2:
    daily_study_time = st.number_input(
        "하루에 공부할 수 있는 시간",
        min_value=0.5,
        max_value=24.0,
        value=5.0,
        step=0.5
    )

total_study_time = days_left * daily_study_time

st.info(
    f"시험까지 총 **{days_left}일** 남았으며, "
    f"총 공부 가능 시간은 **{total_study_time:.1f}시간**입니다."
)

# -----------------------------------
# 과목별 정보
# -----------------------------------

st.header("2. 과목별 중요도와 목표")

st.write(
    "각 과목의 중요도와 이번 시험에서 얼마나 점수를 올리고 싶은지를 입력하세요."
)

subject_info = {}

for subject in subjects:

    with st.expander(f"📖 {subject}", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            importance = st.slider(
                f"{subject} 중요도",
                min_value=1,
                max_value=5,
                value=3,
                key=f"importance_{subject}"
            )

        with col2:
            goal = st.slider(
                f"{subject} 점수 향상 목표",
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
# 계획 생성 버튼
# -----------------------------------

st.header("3. 공부 계획 생성")

if st.button("📅 공부 계획 만들기", type="primary"):

    # -----------------------------------
    # 우선순위 계산
    # -----------------------------------

    for subject in subjects:

        importance = subject_info[subject]["importance"]
        goal = subject_info[subject]["goal"]

        # 현재 기본 알고리즘
        priority = (
            importance * 0.6
            + goal * 0.4
        )

        subject_info[subject]["priority"] = priority

    # -----------------------------------
    # 전체 우선순위 계산
    # -----------------------------------

    total_priority = sum(
        subject_info[subject]["priority"]
        for subject in subjects
    )

    # -----------------------------------
    # 과목별 공부시간 계산
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
    # 우선순위 순으로 정렬
    # -----------------------------------

    sorted_subjects = sorted(
        subjects,
        key=lambda x: subject_info[x]["priority"],
        reverse=True
    )

    # -----------------------------------
    # 결과 출력
    # -----------------------------------

    st.header("4. 분석 결과")

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
            "총 공부시간": round(
                subject_info[subject]["study_time"],
                1
            )
        })

    df = pd.DataFrame(result_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------
    # 가장 우선순위가 높은 과목
    # -----------------------------------

    first_subject = sorted_subjects[0]

    st.success(
        f"현재 입력된 조건에서는 **{first_subject}**의 "
        f"우선순위가 가장 높습니다."
    )

    # -----------------------------------
    # 하루 공부 계획
    # -----------------------------------

    st.header("5. 하루 공부 계획")

    daily_data = []

    for subject in sorted_subjects:

        priority = subject_info[subject]["priority"]

        daily_time = (
            daily_study_time
            * priority
            / total_priority
        )

        daily_data.append({
            "과목": subject,
            "하루 공부시간": f"{daily_time:.1f}시간"
        })

    daily_df = pd.DataFrame(daily_data)

    st.dataframe(
        daily_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------
    # 날짜별 계획
    # -----------------------------------

    st.header("6. 시험 전 전체 계획")

    for day in range(1, days_left + 1):

        with st.expander(f"Day {day}"):

            for subject in sorted_subjects:

                priority = subject_info[subject]["priority"]

                daily_time = (
                    daily_study_time
                    * priority
                    / total_priority
                )

                st.write(
                    f"**{subject}** — {daily_time:.1f}시간"
                )
