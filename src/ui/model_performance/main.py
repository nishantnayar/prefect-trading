"""
Model Performance Dashboard Main Page

This module provides the main render function for the Model Performance dashboard,
orchestrating all the components and providing the overall page structure.
"""

import streamlit as st
from .utils.data_manager import ModelPerformanceManager
from .components.metrics_dashboard import render_metrics_dashboard
from .components.rankings_table import render_rankings_table
from .components.trends_chart import render_trends_chart
from .components.training_history import render_training_history
from .components.performance_analytics import render_performance_analytics
from .components.model_details import render_model_details


def render_model_performance():
    """
    Render the complete Model Performance dashboard page.
    
    This function orchestrates all the components and provides the overall
    page structure with proper error handling and loading states.
    """
    st.title("🤖 Model Performance Dashboard")
    
    # Add page description
    st.markdown("""
    This dashboard provides comprehensive insights into your ML model performance,
    including rankings, trends, training history, and detailed analytics.
    All data is automatically updated after training sessions.
    """)
    
    try:
        # Initialize the data manager
        with st.spinner("Loading model performance data..."):
            manager = ModelPerformanceManager()
        
        # Check if we have any data
        overview_metrics = manager.get_overview_metrics()
        
        if overview_metrics['total_models'] == 0:
            st.warning("""
            **No model performance data found.**
            
            To see data in this dashboard:
            1. Run model training: `python -m src.ml.train_gru_models`
            2. Performance metrics will be automatically saved
            3. Rankings and trends will be updated automatically
            4. Refresh this page to see the results
            """)
            
            # Add a button to run training
            if st.button("🚀 Run Training", help="Start model training to generate performance data"):
                st.info("Training can be started from the command line: `python -m src.ml.train_gru_models`")
            
            return
        
        # Display success message if we have data
        st.success(f"✅ Loaded data for {overview_metrics['total_models']} models")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Overview", 
            "🏆 Rankings", 
            "📊 Trends", 
            "🔄 Training History",
            "📋 Model Details"
        ])
        
        with tab1:
            st.header("📈 Performance Overview")
            render_metrics_dashboard(manager)
            
            # Add performance analytics in the overview tab
            st.header("📊 Performance Analytics")
            render_performance_analytics(manager)
        
        with tab2:
            st.header("🏆 Model Rankings")
            render_rankings_table(manager)
        
        with tab3:
            st.header("📊 Performance Trends")
            render_trends_chart(manager)
        
        with tab4:
            st.header("🔄 Training History")
            render_training_history(manager)
        
        with tab5:
            st.header("📋 Model Details")
            render_model_details(manager)
        
        # Add footer with last updated info
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption(f"📊 Total Models: {overview_metrics['total_models']}")
        
        with col2:
            st.caption(f"📈 Avg F1: {overview_metrics['avg_f1_score']:.4f}")
        
        with col3:
            st.caption("🔄 Auto-refresh: 5 minutes")
        
        # Add refresh button
        if st.button("🔄 Refresh Data", help="Manually refresh all data"):
            st.rerun()
    
    except Exception as e:
        st.error(f"""
        **Error loading Model Performance Dashboard:**
        
        {str(e)}
        
        **Troubleshooting:**
        1. Ensure the database is running and accessible
        2. Check that model performance tables exist
        3. Verify database connection settings
        4. Run training to generate initial data
        """)
        
        # Add helpful information
        with st.expander("🔧 Debug Information", expanded=False):
            st.write("**Database Connection:**")
            try:
                # Test database connection
                test_manager = ModelPerformanceManager()
                test_count = test_manager.get_overview_metrics()['total_models']
                st.success(f"✅ Database connected. Found {test_count} models.")
            except Exception as db_error:
                st.error(f"❌ Database connection failed: {db_error}")
            
            st.write("**Next Steps:**")
            st.write("1. Check database connectivity")
            st.write("2. Run model training to generate data")
            st.write("3. Verify MLflow integration")
            st.write("4. Check database migration status")


def get_page_info():
    """
    Get information about this page for navigation.
    
    Returns:
        Dict with page information
    """
    return {
        "title": "Model Performance",
        "icon": "🤖",
        "description": "Comprehensive model performance tracking and analytics"
    } 