"""
Sistema de Revisión de Inventarios - Perú
Aplicación Streamlit para revisar 40 archivos Excel mensualmente
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import config
from validator import validate_multiple_files
from tracker import FileTracker
from email_sender import EmailSender


# Configuración de la página
st.set_page_config(
    page_title="AB InBev - Revisión de Inventarios Perú",
    page_icon="🍺",
    layout="wide"
)

# Colores corporativos AB InBev
ABINBEV_BLUE = "#003087"
ABINBEV_GOLD = "#FDB71A"
ABINBEV_GREEN = "#28a745"
ABINBEV_RED = "#dc3545"


def load_css():
    """Carga estilos CSS personalizados de AB InBev"""
    try:
        with open('.streamlit/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Si no existe el archivo CSS, continuar sin estilos


def init_session_state():
    """Inicializa el estado de la sesión"""
    if 'tracker' not in st.session_state:
        st.session_state.tracker = FileTracker()
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = {}
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None


def create_or_select_session():
    """UI para crear o seleccionar sesión de revisión"""
    # Branding AB InBev en sidebar
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 1rem 0; background: linear-gradient(135deg, {ABINBEV_BLUE} 0%, {ABINBEV_BLUE} 100%); border-radius: 10px; margin-bottom: 1rem;'>
        <h1 style='color: {ABINBEV_GOLD}; margin: 0; font-size: 2rem;'>🍺</h1>
        <h3 style='color: white; margin: 0.5rem 0 0 0;'>AB InBev</h3>
        <p style='color: {ABINBEV_GOLD}; margin: 0.25rem 0 0 0; font-size: 0.9rem;'>Perú</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.header("📅 Sesión de Revisión")

    # Obtener sesiones existentes
    existing_sessions = st.session_state.tracker.get_all_sessions()

    # Opción para crear nueva sesión
    with st.sidebar.expander("➕ Nueva Sesión", expanded=not existing_sessions):
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Año", min_value=2020, max_value=2030,
                                  value=datetime.now().year, key="year")
        with col2:
            month = st.number_input("Mes", min_value=1, max_value=12,
                                   value=datetime.now().month, key="month")

        if st.button("Crear Sesión"):
            session_id = st.session_state.tracker.create_session(year, month)
            st.session_state.current_session = session_id
            st.success(f"Sesión {session_id} creada")
            st.rerun()

    # Seleccionar sesión existente
    if existing_sessions:
        st.sidebar.subheader("📂 Sesiones Existentes")
        selected = st.sidebar.selectbox(
            "Seleccionar sesión:",
            options=existing_sessions,
            index=0 if st.session_state.current_session is None
                  else existing_sessions.index(st.session_state.current_session)
                  if st.session_state.current_session in existing_sessions else 0
        )
        st.session_state.current_session = selected


def display_session_dashboard():
    """Muestra el dashboard de la sesión actual"""
    if st.session_state.current_session is None:
        st.warning("⚠️ Selecciona o crea una sesión para comenzar")
        return

    session_id = st.session_state.current_session
    status = st.session_state.tracker.get_session_status(session_id)

    if status is None:
        st.error("Error al cargar la sesión")
        return

    # Header con branding AB InBev
    st.markdown(f"""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {ABINBEV_BLUE} 0%, #004ba0 100%); border-radius: 15px; margin-bottom: 1rem;'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>📊 Revisión de Inventarios</h1>
        <p style='color: {ABINBEV_GOLD}; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold;'>{session_id}</p>
    </div>
    """, unsafe_allow_html=True)

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🍺 Total Esperados", status["total_expected"])

    with col2:
        st.metric("✅ Recibidos", status["total_received"],
                 delta=f"+{status['total_received']}")

    with col3:
        st.metric("⏳ Faltantes", status["total_missing"],
                 delta=f"-{status['total_missing']}")

    with col4:
        st.metric("🎯 Completado", f"{status['completion_percentage']:.1f}%")

    # Barra de progreso
    st.progress(status['completion_percentage'] / 100)

    # Gráfico de estado
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=['Recibidos', 'Faltantes'],
            values=[status['total_received'], status['total_missing']],
            hole=.3,
            marker_colors=[ABINBEV_GOLD, ABINBEV_RED],
            textfont=dict(size=14, color='white')
        )])
        fig.update_layout(
            title={
                'text': "Estado de Archivos",
                'font': {'size': 18, 'color': ABINBEV_BLUE}
            },
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📋 Estado")
        if status['total_missing'] == 0:
            st.success("✅ Todos los archivos recibidos")
        else:
            st.warning(f"⚠️ {status['total_missing']} archivos pendientes")

        # Mostrar últimos uploads
        if status['uploads']:
            st.caption("Último upload:")
            last_upload = status['uploads'][-1]
            st.text(f"{len(last_upload['files'])} archivos")
            st.caption(datetime.fromisoformat(last_upload['timestamp']).strftime("%d/%m/%Y %H:%M"))


def upload_files_section():
    """Sección para subir archivos"""
    if st.session_state.current_session is None:
        return

    st.markdown("---")
    st.header("🍺 Cargar Archivos Excel")

    uploaded_files = st.file_uploader(
        "Arrastra o selecciona los archivos Excel",
        type=['xlsx', 'xls'],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(f"🍺 {len(uploaded_files)} archivo(s) cargado(s)")

        if st.button("🔍 Validar Archivos", type="primary"):
            with st.spinner("Validando archivos..."):
                # Leer archivos
                files_dict = {}
                for file in uploaded_files:
                    try:
                        df = pd.read_excel(file)
                        files_dict[file.name] = df
                    except Exception as e:
                        st.error(f"Error al leer {file.name}: {str(e)}")

                # Guardar en session state
                st.session_state.uploaded_data = files_dict

                # Validar archivos
                validation_results = validate_multiple_files(files_dict)
                st.session_state.validation_results = validation_results

                # Registrar en el tracker
                st.session_state.tracker.register_upload(
                    st.session_state.current_session,
                    list(files_dict.keys())
                )

                st.success("✅ Validación completada")
                st.rerun()


def display_email_form():
    """Muestra el formulario para enviar reporte por email"""
    st.markdown("---")
    st.subheader("📧 Enviar Reporte por Email")

    # Verificar configuración de email
    email_sender = EmailSender()

    if not email_sender.configured:
        st.error("""
        ⚠️ **Configuración de email no encontrada**

        Para enviar emails, debes configurar el archivo `.streamlit/secrets.toml` con tus credenciales SMTP.

        Ver `.streamlit/secrets.toml.example` para más detalles.
        """)
        if st.button("❌ Cerrar"):
            st.session_state.show_email_form = False
            st.rerun()
        return

    # Formulario
    with st.form("email_form"):
        # Destinatarios
        recipients_input = st.text_area(
            "Destinatarios (uno por línea)",
            value="\n".join(config.DEFAULT_RECIPIENTS),
            help="Ingresa los emails de los destinatarios, uno por línea"
        )

        # CC (opcional)
        cc_input = st.text_area(
            "CC - Con copia (opcional, uno por línea)",
            value="\n".join(config.DEFAULT_CC) if config.DEFAULT_CC else "",
            help="Emails que recibirán copia del reporte"
        )

        # Botones
        col1, col2 = st.columns(2)

        with col1:
            submit = st.form_submit_button("✉️ Enviar Email", type="primary")

        with col2:
            cancel = st.form_submit_button("❌ Cancelar")

        if cancel:
            st.session_state.show_email_form = False
            st.rerun()

        if submit:
            # Procesar emails
            recipients = [email.strip() for email in recipients_input.split('\n') if email.strip()]
            cc = [email.strip() for email in cc_input.split('\n') if email.strip()] if cc_input else []

            if not recipients:
                st.error("⚠️ Debes ingresar al menos un destinatario")
                return

            # Obtener datos necesarios
            session_status = st.session_state.tracker.get_session_status(
                st.session_state.current_session
            )
            validation_results = st.session_state.validation_results
            missing_files = st.session_state.tracker.get_missing_files(
                st.session_state.current_session
            )

            # Generar reporte Excel
            report_data = generate_validation_report(validation_results)

            # Enviar email
            with st.spinner("Enviando email..."):
                success = email_sender.send_report(
                    recipients=recipients,
                    cc=cc,
                    session_id=st.session_state.current_session,
                    session_status=session_status,
                    validation_results=validation_results,
                    missing_files=missing_files,
                    attachment_data=report_data
                )

            if success:
                st.success(f"✅ Email enviado exitosamente a {len(recipients)} destinatario(s)")
                st.session_state.show_email_form = False
                st.balloons()
            else:
                st.error("❌ Error al enviar el email. Verifica la configuración SMTP.")


def display_validation_results():
    """Muestra los resultados de la validación"""
    if st.session_state.validation_results is None:
        return

    st.markdown("---")
    st.header("✅ Resultados de Validación")

    results = st.session_state.validation_results
    summary = results["summary"]

    # Métricas de validación
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Archivos Validados", summary["total_files"])

    with col2:
        st.metric("Archivos Válidos", summary["valid_files"],
                 delta=f"{summary['valid_files']}")

    with col3:
        st.metric("Archivos con Errores", summary["invalid_files"],
                 delta=f"-{summary['invalid_files']}" if summary['invalid_files'] > 0 else None)

    with col4:
        st.metric("Total Errores", summary["total_errors"])

    # Tabla de resultados detallados
    st.subheader("📋 Detalle por Archivo")

    for result in results["results"]:
        with st.expander(f"{'✅' if result['is_valid'] else '❌'} {result['filename']} ({result['total_rows']} filas)"):
            if result['errors']:
                st.error("**Errores:**")
                for error in result['errors']:
                    st.write(f"- {error}")

            if result['warnings']:
                st.warning("**Advertencias:**")
                for warning in result['warnings']:
                    st.write(f"- {warning}")

            if not result['errors'] and not result['warnings']:
                st.success("Sin errores ni advertencias")

            # Mostrar preview de datos
            if result['filename'] in st.session_state.uploaded_data:
                st.caption("Vista previa de datos:")
                st.dataframe(
                    st.session_state.uploaded_data[result['filename']].head(5),
                    use_container_width=True
                )

    # Botones de exportación y envío
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Exportar Reporte de Validación"):
            report = generate_validation_report(results)
            st.download_button(
                "⬇️ Descargar Reporte",
                data=report,
                file_name=f"reporte_validacion_{st.session_state.current_session}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col2:
        if st.button("📧 Enviar Reporte por Email", type="primary"):
            st.session_state.show_email_form = True

    # Formulario de envío de email
    if st.session_state.get('show_email_form', False):
        display_email_form()


def display_missing_files():
    """Muestra la lista de archivos faltantes"""
    if st.session_state.current_session is None:
        return

    st.markdown("---")
    st.header("🍺⏳ Archivos Faltantes")

    missing = st.session_state.tracker.get_missing_files(
        st.session_state.current_session
    )

    if not missing:
        st.success("✅ No hay archivos faltantes")
        return

    st.warning(f"⚠️ {len(missing)} archivo(s) faltante(s)")

    # Mostrar lista de faltantes
    df_missing = pd.DataFrame({"Archivo Faltante": missing})
    st.dataframe(df_missing, use_container_width=True, hide_index=True)

    # Botón para exportar lista de faltantes
    csv = df_missing.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Descargar Lista de Faltantes",
        data=csv,
        file_name=f"faltantes_{st.session_state.current_session}.csv",
        mime="text/csv"
    )


def generate_validation_report(validation_results) -> bytes:
    """Genera un reporte Excel con los resultados de validación"""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Resumen
        summary_df = pd.DataFrame([validation_results["summary"]])
        summary_df.to_excel(writer, sheet_name='Resumen', index=False)

        # Detalle por archivo
        details = []
        for result in validation_results["results"]:
            details.append({
                "Archivo": result["filename"],
                "Total Filas": result["total_rows"],
                "Válido": "Sí" if result["is_valid"] else "No",
                "Errores": len(result["errors"]),
                "Advertencias": len(result["warnings"]),
                "Detalle Errores": "; ".join(result["errors"]),
                "Detalle Advertencias": "; ".join(result["warnings"])
            })

        details_df = pd.DataFrame(details)
        details_df.to_excel(writer, sheet_name='Detalle', index=False)

    output.seek(0)
    return output.getvalue()


def main():
    """Función principal de la aplicación"""
    # Cargar estilos personalizados AB InBev
    load_css()

    init_session_state()

    # Sidebar para selección de sesión
    create_or_select_session()

    # Contenido principal
    display_session_dashboard()
    upload_files_section()
    display_validation_results()
    display_missing_files()

    # Footer con branding AB InBev
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px;'>
        <p style='color: {ABINBEV_BLUE}; margin: 0; font-weight: bold;'>AB InBev Perú</p>
        <p style='color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Sistema de Revisión de Inventarios v1.0</p>
        <p style='color: {ABINBEV_GOLD}; margin: 0.25rem 0 0 0; font-size: 0.85rem; font-weight: bold;'>Día de revisión: 9 de cada mes</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
