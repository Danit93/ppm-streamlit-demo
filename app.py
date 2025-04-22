import streamlit as st
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="PPM (Appix style)", layout="wide")

# ───────────────────────────────── Helpers
def init_store()
    d = st.session_state
    if projects not in d
        d.projects, d.stages, d.tasks, d.resources = [], [], [], []
def gid(prefix str) - str
    return f{prefix}_{int(datetime.now().timestamp()1e3)}
init_store()

# ───────────────────────────────── Sidebar nav
page = st.sidebar.radio(
    Навигация,
    (Dashboard, Projects, Stages, Tasks, Resources),
    label_visibility=collapsed,
)
st.sidebar.markdown(---)
st.sidebar.write(© PPM Prototype on Streamlit)

# ───────────────────────────────── Dashboard
if page == Dashboard
    st.title(Dashboard  Portfolio KPI)
    col1, col2, col3 = st.columns(3)
    col1.metric(Проектов, len(st.session_state.projects))
    col2.metric(Задач, len(st.session_state.tasks))
    col3.metric(Ресурсов, len(st.session_state.resources))

    # Burndown by task span
    spans = [
        max(
            (
                datetime.strptime(t[end], %Y-%m-%d)
                - datetime.strptime(t[start], %Y-%m-%d)
            ).days,
            0,
        )
        for t in st.session_state.tasks
    ]
    if spans
        st.subheader(Длительность задач (дни))
        st.bar_chart(pd.DataFrame({span spans}))
    # Resource availability
    if st.session_state.resources
        st.subheader(Доступность ресурсов, %)
        df = pd.DataFrame(st.session_state.resources).set_index(name)
        st.bar_chart(df[avail])

# ───────────────────────────────── Projects
elif page == Projects
    st.title(Projects)
    with st.form(add_proj, clear_on_submit=True)
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 2, 2])
        name = c1.text_input(Name)
        sponsor = c2.text_input(Sponsor)
        status = c3.selectbox(Status, [Active, On Hold, Completed])
        start = c4.date_input(Start, date.today())
        end_plan = c5.date_input(
            Planned End, date.today() + relativedelta(months=6)
        )
        submitted = st.form_submit_button(Add)
        if submitted
            st.session_state.projects.append(
                dict(
                    id=gid(pr),
                    name=name,
                    sponsor=sponsor,
                    status=status,
                    start=start.isoformat(),
                    endPlan=end_plan.isoformat(),
                )
            )

    if st.session_state.projects
        df = pd.DataFrame(st.session_state.projects)
        st.dataframe(df, use_container_width=True)

        # open project card
        sel = st.selectbox(
            Открыть карточку проекта,
            options=df[id],
            format_func=lambda x df.set_index(id).loc[x, name],
        )
        if st.button(➡ Open)
            st.session_state.page = CARD
            st.session_state.current_project = sel
            st.experimental_rerun()

# ───────────────────────────────── Project Card
elif st.session_state.get(page) == CARD
    pid = st.session_state.current_project
    proj = next(p for p in st.session_state.projects if p[id] == pid)
    st.markdown(f### {proj['name']} &nbsp;·&nbsp; {proj['status']})
    st.write(
        fSponsor {proj['sponsor'] or '—'}   
        fStart {proj['start']}   Planned End {proj['endPlan']}
    )

    # stages
    st.subheader(Stages)
    with st.form(add_stage, clear_on_submit=True)
        sname, sowner = st.columns([3, 2])
        stg_name = sname.text_input(Stage name)
        stg_owner = sowner.text_input(Owner)
        if st.form_submit_button(Add stage)
            st.session_state.stages.append(
                dict(
                    id=gid(st),
                    project=pid,
                    name=stg_name,
                    owner=stg_owner,
                )
            )
    st.dataframe(
        pd.DataFrame(
            [s for s in st.session_state.stages if s[project] == pid]
        ),
        use_container_width=True,
    )

    # tasks
    st.subheader(Tasks)
    proj_stages = [s for s in st.session_state.stages if s[project] == pid]
    if proj_stages
        with st.form(add_task, clear_on_submit=True)
            cs1, cs2, cs3, cs4, cs5 = st.columns([3, 2, 2, 2, 1])
            stage_sel = cs1.selectbox(
                Stage,
                proj_stages,
                format_func=lambda x x[name],
            )
            tname = cs2.text_input(Task name)
            start_d = cs3.date_input(Start, date.today(), key=ts_s)
            end_d = cs4.date_input(End, date.today() + relativedelta(weeks=1))
            eff = cs5.number_input(Effort h, 1, 1000, 8)
            if st.form_submit_button(Add task)
                st.session_state.tasks.append(
                    dict(
                        id=gid(ts),
                        stage=stage_sel[id],
                        name=tname,
                        assignee=,
                        start=start_d.isoformat(),
                        end=end_d.isoformat(),
                        effort=eff,
                    )
                )
    # tasks table + assign button
    tasks = [
        t
        for t in st.session_state.tasks
        if any(s[id] == t[stage] for s in proj_stages)
    ]
    if tasks
        df = pd.DataFrame(tasks)
        df_display = df.copy()
        df_display[stage] = df_display[stage].map(
            {s[id] s[name] for s in proj_stages}
        )
        st.dataframe(df_display, use_container_width=True)
        sel_task = st.selectbox(
            Assign resource for task,
            options=df[id],
            format_func=lambda x df.set_index(id).loc[x, name],
        )
        if st.button(🔗 Assign auto)
            free = (
                pd.DataFrame(st.session_state.resources)
                .sort_values(avail, ascending=False)
                .query(avail  0)
            )
            if free.empty
                st.warning(Нет свободных ресурсов)
            else
                res = free.iloc[0]
                task = next(t for t in st.session_state.tasks if t[id] == sel_task)
                task[assignee] = res[name]
                res[avail] = max(0, res[avail] - 10)
                st.success(f{res['name']} назначен на задачу)
                st.experimental_rerun()

    if st.button(← Back)
        st.session_state.page = None
        st.experimental_rerun()

# ───────────────────────────────── Stages
elif page == Stages
    st.title(Stages)
    if not st.session_state.projects
        st.info(Сначала создайте проект)
    else
        with st.form(add_stg, clear_on_submit=True)
            prj = st.selectbox(
                Project, st.session_state.projects, format_func=lambda x x[name]
            )
            name = st.text_input(Stage name)
            owner = st.text_input(Owner)
            if st.form_submit_button(Add)
                st.session_state.stages.append(
                    dict(id=gid(st), project=prj[id], name=name, owner=owner)
                )
        st.dataframe(pd.DataFrame(st.session_state.stages), use_container_width=True)

# ───────────────────────────────── Tasks
elif page == Tasks
    st.title(Tasks)
    st.dataframe(pd.DataFrame(st.session_state.tasks), use_container_width=True)

# ───────────────────────────────── Resources
elif page == Resources
    st.title(Resources)
    with st.form(add_res, clear_on_submit=True)
        c1, c2, c3 = st.columns([3, 2, 2])
        name = c1.text_input(Name)
        rate = c2.number_input(Rate per h, 1, 10000, 100)
        avail = c3.number_input(Availability %, 0, 100, 80)
        if st.form_submit_button(Add)
            st.session_state.resources.append(
                dict(id=gid(rs), name=name, rate=rate, avail=avail)
            )
    st.dataframe(pd.DataFrame(st.session_state.resources), use_container_width=True)
