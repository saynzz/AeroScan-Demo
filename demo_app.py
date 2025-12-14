import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(
    page_title="AeroScan Engine | Демо",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Основные стили */
    .main {
        padding: 0 2rem;
        background-color: #0a0a0f;
        color: #e0e0e0;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    /* Заголовки */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00c896 0%, #00a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        border-left: 4px solid #00c896;
        padding-left: 1rem;
        margin: 2.5rem 0 1.5rem 0;
    }
    
    .subsection-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #00c896;
        margin: 1.5rem 0 0.8rem 0;
    }
    
    /* Карточки */
    .card {
        background: rgba(30, 30, 40, 0.7);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 200, 150, 0.1), rgba(0, 168, 255, 0.05));
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(0, 200, 150, 0.2);
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #00c896 0%, #009975 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    /* Убираем лишние элементы */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

if 'process_step' not in st.session_state:
    st.session_state.process_step = 1
if 'project_data' not in st.session_state:
    st.session_state.project_data = None
if 'defects_found' not in st.session_state:
    st.session_state.defects_found = []
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False

def generate_sample_data():
    """Генерация реалистичных тестовых данных"""
    np.random.seed(42)
    n_defects = 27
    
    defects = []
    for i in range(n_defects):
        defect_type = np.random.choice(['Яма', 'Трещина', 'Просадка', 'Выбоина', 'Колейность'], 
                                       p=[0.4, 0.25, 0.15, 0.1, 0.1])
        
        if defect_type == 'Яма':
            depth = np.random.uniform(8, 45)
            width = np.random.uniform(40, 200)
        elif defect_type == 'Трещина':
            depth = np.random.uniform(2, 15)
            width = np.random.uniform(5, 50)
        else:
            depth = np.random.uniform(5, 25)
            width = np.random.uniform(30, 120)
        
        severity = 'Высокая' if depth > 20 else ('Средняя' if depth > 10 else 'Низкая')
        
        defects.append({
            'ID': i+1,
            'Тип дефекта': defect_type,
            'Глубина (см)': round(depth, 1),
            'Ширина (см)': round(width, 1),
            'Критичность': severity,
            'Координаты X': round(np.random.uniform(125000, 127000), 2),
            'Координаты Y': round(np.random.uniform(456000, 458000), 2),
            'Рекомендация': 'Срочный ремонт' if severity == 'Высокая' else 'Плановый ремонт'
        })
    
    return pd.DataFrame(defects)

def create_3d_point_cloud():
    """Создание 3D визуализации дороги с дефектами"""
    np.random.seed(42)
    
    x = np.linspace(-50, 50, 100)
    y = np.linspace(-20, 20, 50)
    X, Y = np.meshgrid(x, y)
    Z = 0.1 * np.sin(0.3*X) * np.cos(0.2*Y)
    
    defect_locations = [(-30, -5), (10, 8), (35, -12)]
    for xc, yc in defect_locations:
        idx_x = np.argmin(np.abs(x - xc))
        idx_y = np.argmin(np.abs(y - yc))
        Z[idx_y-5:idx_y+5, idx_x-5:idx_x+5] -= np.random.uniform(1, 3)
    
    fig = go.Figure(data=[
        go.Surface(
            z=Z,
            x=X,
            y=Y,
            colorscale='Viridis',
            opacity=0.9,
            contours={
                "z": {"show": True, "usecolormap": True, "highlightcolor": "limegreen", "project": {"z": True}}
            },
            name="Поверхность дороги"
        )
    ])
    
    defect_df = generate_sample_data()
    critical_defects = defect_df[defect_df['Критичность'] == 'Высокая'].head(3)
    
    for _, defect in critical_defects.iterrows():
        fig.add_trace(go.Scatter3d(
            x=[defect['Координаты X'] % 100 - 50],
            y=[defect['Координаты Y'] % 40 - 20],
            z=[-defect['Глубина (см)']/10 - 0.5],
            mode='markers',
            marker=dict(
                size=defect['Ширина (см)']/5,
                color='red',
                symbol='diamond',
                line=dict(color='white', width=2)
            ),
            name=f"Дефект {defect['ID']}",
            hovertemplate=f"<b>Дефект {defect['ID']}</b><br>Тип: {defect['Тип дефекта']}<br>Глубина: {defect['Глубина (см)']} см<br>Критичность: {defect['Критичность']}<extra></extra>"
        ))
    
    fig.update_layout(
        title={
            'text': "3D Модель карьерной дороги с выделенными дефектами",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': 'white'}
        },
        scene=dict(
            xaxis_title='Длина, м',
            yaxis_title='Ширина, м',
            zaxis_title='Высота, м',
            bgcolor='rgba(10, 10, 15, 1)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1)
            )
        ),
        width=900,
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(30, 30, 40, 0.8)'
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )
    
    return fig

st.markdown('<div class="main">', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">AeroScan Engine</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #aaa; font-size: 1.1rem; margin-bottom: 2rem;">Программный комплекс для автоматизированного мониторинга карьерных дорог</p>', unsafe_allow_html=True)

st.markdown('<h2 class="section-title">Рабочий процесс анализа</h2>', unsafe_allow_html=True)

step_cols = st.columns(3)
with step_cols[0]:
    step1_color = "#00c896" if st.session_state.process_step >= 1 else "#444"
    st.markdown(f'<div class="metric-card" style="border-color: {step1_color}"><h3>1</h3><p>Загрузка данных</p></div>', unsafe_allow_html=True)
with step_cols[1]:
    step2_color = "#00c896" if st.session_state.process_step >= 2 else "#444"
    st.markdown(f'<div class="metric-card" style="border-color: {step2_color}"><h3>2</h3><p>Обработка</p></div>', unsafe_allow_html=True)
with step_cols[2]:
    step3_color = "#00c896" if st.session_state.process_step >= 3 else "#444"
    st.markdown(f'<div class="metric-card" style="border-color: {step3_color}"><h3>3</h3><p>Результаты</p></div>', unsafe_allow_html=True)

st.markdown("---")


if st.session_state.process_step == 1:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown('<h3 class="subsection-title">Загрузка данных проекта</h3>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Перетащите или выберите файлы данных дрона",
            type=['jpg', 'png', 'tif', 'las', 'laz', 'obj'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.success(f"Загружено {len(uploaded_files)} файлов")
            
            with st.expander("Детали проекта", expanded=True):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.text_input("Название проекта", value="Карьер 'Восточный'", key="project_name")
                    st.text_input("Дата съёмки", value=datetime.now().strftime("%d.%m.%Y"), key="survey_date")
                with col_info2:
                    st.number_input("Длина дороги (км)", min_value=0.1, max_value=50.0, value=8.2, step=0.1, key="road_length")
                    st.selectbox("Тип покрытия", ["Грунтовая", "Щебёночная", "Асфальтовая"], key="road_type")
        
        if st.button("Начать обработку данных", type="primary", use_container_width=True):
            st.session_state.process_step = 2
            st.session_state.project_data = generate_sample_data()
            st.rerun()
    
    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: #00c896;">Возможности</h4>', unsafe_allow_html=True)
        st.markdown("• **Фотограмметрия ODM**")
        st.markdown("• **AI-детекция дефектов**")
        st.markdown("• **SLAM-ускорение**")
        st.markdown("• **Геопривязка**")
        st.markdown("• **Экспорт отчетов**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card" style="margin-top: 1rem;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: #00c896;">Быстрый старт</h4>', unsafe_allow_html=True)
        if st.button("Использовать тестовые данные", use_container_width=True, key="test_data"):
            st.session_state.process_step = 2
            st.session_state.project_data = generate_sample_data()
            st.success("Тестовые данные загружены")
            time.sleep(0.5)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ----- ШАГ 2: ОБРАБОТКА -----
elif st.session_state.process_step == 2:
    st.markdown('<h3 class="subsection-title">Обработка данных</h3>', unsafe_allow_html=True)
    
    processing_steps = [
        "Чтение данных дрона...",
        "Калибровка камер...",
        "Построение 3D модели...",
        "SLAM-реконструкция...",
        "AI-анализ дефектов...",
        "Геопривязка результатов...",
        "Генерация отчёта..."
    ]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, step in enumerate(processing_steps):
        status_text.markdown(f'{step}', unsafe_allow_html=True)
        progress_bar.progress((i + 1) / len(processing_steps))
        time.sleep(0.5)
    
    status_text.markdown('Обработка завершена успешно!', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<h3 class="subsection-title">Ключевые метрики</h3>', unsafe_allow_html=True)
    
    metric_cols = st.columns(4)
    metrics = [
        ("Время обработки", "1 ч 18 мин", "#00c896"),
        ("Точность", "87.4%", "#00a8ff"),
        ("Дефектов", "27", "#ff6b6b"),
        ("Критических", "5", "#ff4757")
    ]
    
    for idx, (title, value, color) in enumerate(metrics):
        with metric_cols[idx]:
            st.markdown(f'''
            <div class="metric-card" style="border-color: {color};">
                <h3 style="color: {color}; margin: 0; font-size: 2rem;">{value}</h3>
                <p style="margin: 0; color: #aaa;">{title}</p>
            </div>
            ''', unsafe_allow_html=True)
    
    if st.button("Перейти к результатам", type="primary", use_container_width=True):
        st.session_state.process_step = 3
        st.rerun()

# ----- ШАГ 3: РЕЗУЛЬТАТЫ -----
elif st.session_state.process_step == 3:
    tab1, tab2, tab3, tab4 = st.tabs(["3D Визуализация", "Данные дефектов", "Аналитика", "Отчёт"])
    
    with tab1:
        st.markdown('<h3 class="subsection-title">3D Модель карьерной дороги</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #aaa;">Интерактивная модель с выделенными дефектами</p>', unsafe_allow_html=True)
        
        fig_3d = create_3d_point_cloud()
        st.plotly_chart(fig_3d, use_container_width=True)
        
        col_legend, col_controls = st.columns([2, 1])
        with col_legend:
            st.markdown('''
            <div class="card">
                <h4 style="color: #00c896;">Обозначения:</h4>
                <p>• <span style="color: #00c896;">Поверхность</span> - 3D модель дороги</p>
                <p>• <span style="color: red;">Красные ромбы</span> - критические дефекты</p>
            </div>
            ''', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h3 class="subsection-title">Детектированные дефекты</h3>', unsafe_allow_html=True)
        
        if st.session_state.project_data is not None:
            defects_df = st.session_state.project_data
            
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                defect_types = st.multiselect("Тип дефекта", options=defects_df['Тип дефекта'].unique(), default=defects_df['Тип дефекта'].unique())
            with col_filter2:
                severity_filter = st.multiselect("Критичность", options=defects_df['Критичность'].unique(), default=defects_df['Критичность'].unique())
            
            filtered_df = defects_df[
                (defects_df['Тип дефекта'].isin(defect_types)) &
                (defects_df['Критичность'].isin(severity_filter))
            ]
            
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            export_col1, export_col2 = st.columns(2)
            with export_col1:
                if st.button("Экспорт в CSV", use_container_width=True):
                    st.success("CSV файл готов")
            with export_col2:
                if st.button("Экспорт в DXF", use_container_width=True):
                    st.success("DXF файл готов")
    
    with tab3:
        st.markdown('<h3 class="subsection-title">Аналитическая панель</h3>', unsafe_allow_html=True)
        
        if st.session_state.project_data is not None:
            defects_df = st.session_state.project_data
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                type_counts = defects_df['Тип дефекта'].value_counts()
                fig1 = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Распределение по типам",
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                fig2 = px.histogram(
                    defects_df,
                    x='Глубина (см)',
                    color='Критичность',
                    title="Распределение по глубине",
                    color_discrete_map={
                        'Низкая': '#00c896',
                        'Средняя': '#ffa502',
                        'Высокая': '#ff4757'
                    }
                )
                st.plotly_chart(fig2, use_container_width=True)
    
    with tab4:
        st.markdown('<h3 class="subsection-title">Генерация отчёта</h3>', unsafe_allow_html=True)
        
        col_report_left, col_report_right = st.columns([2, 1])
        
        with col_report_left:
            report_content = f"""
            # ТЕХНИЧЕСКИЙ ОТЧЁТ
            **Объект:** Карьер "Восточный"  
            **Дата:** {datetime.now().strftime("%d.%m.%Y")}  
            
            ## РЕЗЮМЕ
            - **Протяжённость:** 8.2 км
            - **Дефектов найдено:** 27
            - **Критических:** 5
            
            ## РЕКОМЕНДАЦИИ
            - **Приоритет 1:** Ремонт критических дефектов
            - **Приоритет 2:** Плановый ремонт остальных
            """
            
            st.text_area("Содержимое отчёта", report_content, height=300, disabled=True)
        
        with col_report_right:
            report_format = st.selectbox("Формат", ["PDF", "DOCX", "HTML"])
            
            if st.button("Сгенерировать отчёт", type="primary", use_container_width=True):
                st.session_state.report_generated = True
                st.success(f"Отчёт в формате {report_format} готов!")
    
    if st.button("Начать новый проект", use_container_width=True):
        st.session_state.process_step = 1
        st.session_state.project_data = None
        st.session_state.report_generated = False
        st.rerun()

st.markdown("---")
st.markdown('<div style="text-align: center; color: #666; font-size: 0.9rem;">© 2025 AeroScan 3D. DEMO VERSION.</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)