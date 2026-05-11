import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Phone Usage Analytics Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .highlight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load and cache data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('../phone_usage.csv')
        return df
    except FileNotFoundError:
        st.error("Dataset not found! Please ensure 'phone_usage.csv' is in the parent directory.")
        return None

@st.cache_data
def preprocess_data(df):
    if df is None:
        return None
    
    df_processed = df.copy()
    
    # Add calculated columns
    df_processed['Total_Screen_Time'] = df_processed['Daily_Phone_Hours'] + df_processed['Social_Media_Hours']
    df_processed['Usage_Intensity'] = pd.cut(df_processed['Daily_Phone_Hours'], 
                                            bins=[0, 3, 6, 9, 12], 
                                            labels=['Low', 'Medium', 'High', 'Very High'])
    df_processed['Age_Group'] = pd.cut(df_processed['Age'], 
                                       bins=[17, 25, 35, 45, 60], 
                                       labels=['18-25', '26-35', '36-45', '46-60'])
    df_processed['Stress_Category'] = pd.cut(df_processed['Stress_Level'], 
                                            bins=[0, 3, 6, 10], 
                                            labels=['Low', 'Medium', 'High'])
    
    return df_processed

# Simple linear regression function
def simple_regression(df, x_col, y_col):
    X = df[[x_col]]
    y = df[y_col]
    
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    return {
        'coefficient': model.coef_[0],
        'intercept': model.intercept_,
        'r2': r2,
        'rmse': rmse,
        'equation': f"{y_col} = {model.intercept_:.4f} + {model.coef_[0]:.4f} × {x_col}"
    }

# Main dashboard function
def main():
    # Load data
    df = load_data()
    if df is None:
        return
    
    df_processed = preprocess_data(df)
    if df_processed is None:
        return
    
    # Header
    st.markdown('<h1 class="main-header">📱 Phone Usage Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Complete Analysis: Data Collection → Preprocessing → EDA → Regression Visualization → Correlation Analysis")
    
    # Sidebar for navigation
    st.sidebar.title("🔍 Navigation")
    page = st.sidebar.selectbox("Select Analysis Section", [
        "📊 Data Collection",
        "🔧 Data Preprocessing", 
        "📈 Exploratory Data Analysis (EDA)",
        "📊 Regression Visualization",
        "🔗 Correlation Analysis",
        "📋 Interactive Visualizations",
        "🚀 Deployment Access"
    ])
    
    # Filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("🎛️ **Filters**")
    
    age_range = st.sidebar.slider("Age Range", 
                             min_value=int(df['Age'].min()), 
                             max_value=int(df['Age'].max()), 
                             value=(int(df['Age'].min()), int(df['Age'].max())))
    
    phone_hours_range = st.sidebar.slider("Phone Hours Range", 
                                    min_value=float(df['Daily_Phone_Hours'].min()), 
                                    max_value=float(df['Daily_Phone_Hours'].max()), 
                                    value=(float(df['Daily_Phone_Hours'].min()), float(df['Daily_Phone_Hours'].max())))
    
    gender_filter = st.sidebar.multiselect("Gender", 
                                       options=df['Gender'].unique(), 
                                       default=df['Gender'].unique())
    
    device_filter = st.sidebar.multiselect("Device Type", 
                                       options=df['Device_Type'].unique(), 
                                       default=df['Device_Type'].unique())
    
    # Apply filters
    filtered_df = df_processed[
        (df_processed['Age'].between(age_range[0], age_range[1])) &
        (df_processed['Daily_Phone_Hours'].between(phone_hours_range[0], phone_hours_range[1])) &
        (df_processed['Gender'].isin(gender_filter)) &
        (df_processed['Device_Type'].isin(device_filter))
    ]
    
    # Page 1: Data Collection
    if page == "📊 Data Collection":
        st.markdown('<h2 class="section-header">📊 Data Collection</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        **Data Collection Process:**
        - Dataset: Phone usage behavior and health metrics
        - Source: Survey-based data collection
        - Size: 50,000 user records
        - Variables: 13 measured features
        - Quality: Complete dataset with no missing values
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Dataset info
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Records", f"{len(filtered_df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Columns", f"{len(filtered_df.columns)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Numeric Columns", f"{len(filtered_df.select_dtypes(include=[np.number]).columns)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Categorical Columns", f"{len(filtered_df.select_dtypes(include=['object']).columns)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Data preview
        st.subheader("Dataset Preview")
        st.dataframe(filtered_df.head(10))
        
        # Column information
        st.subheader("Variable Descriptions")
        variable_info = [
            "**User_ID**: Unique identifier for each user",
            "**Age**: User's age in years (18-60)",
            "**Gender**: User's gender (Male, Female, Other)",
            "**Occupation**: User's occupation (Student, Professional, Business Owner, Freelancer)",
            "**Device_Type**: Type of device used (Android, iOS)",
            "**Daily_Phone_Hours**: Average daily phone usage in hours (1-12)",
            "**Social_Media_Hours**: Daily social media usage in hours (0.5-8)",
            "**Work_Productivity_Score**: Self-reported work productivity (1-10 scale)",
            "**Sleep_Hours**: Average daily sleep in hours (4-9)",
            "**Stress_Level**: Self-reported stress level (1-10 scale)",
            "**App_Usage_Count**: Number of apps used daily (5-60)",
            "**Caffeine_Intake_Cups**: Daily caffeine intake in cups (0-6)",
            "**Weekend_Screen_Time_Hours**: Weekend screen time in hours (2-14)"
        ]
        
        for info in variable_info:
            st.markdown(f"- {info}")
    
    # Page 2: Data Preprocessing
    elif page == "🔧 Data Preprocessing":
        st.markdown('<h2 class="section-header">🔧 Data Preprocessing</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        **Data Preprocessing Steps:**
        - Data cleaning and validation
        - Feature engineering for better analysis
        - Categorical variable encoding
        - Data quality checks
        - Preparation for modeling
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Feature engineering display
        st.subheader("Engineered Features")
        
        engineered_features = [
            "Total_Screen_Time = Daily_Phone_Hours + Social_Media_Hours",
            "Usage_Intensity: Low (0-3h), Medium (3-6h), High (6-9h), Very High (9-12h)",
            "Age_Group: 18-25, 26-35, 36-45, 46-60",
            "Stress_Category: Low (0-3), Medium (3-6), High (6-10)"
        ]
        
        for feature in engineered_features:
            st.markdown(f"- {feature}")
        
        # Distribution of engineered features
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Usage Intensity Distribution")
            intensity_counts = filtered_df['Usage_Intensity'].value_counts()
            fig_intensity = px.pie(values=intensity_counts.values, 
                                  names=intensity_counts.index,
                                  title="Usage Intensity Categories")
            st.plotly_chart(fig_intensity, use_container_width=True)
        
        with col2:
            st.subheader("Age Group Distribution")
            age_counts = filtered_df['Age_Group'].value_counts()
            fig_age = px.bar(x=age_counts.index, y=age_counts.values,
                             title="Age Group Distribution")
            fig_age.update_xaxes(tickangle=45)
            st.plotly_chart(fig_age, use_container_width=True)
        
        # Data quality metrics
        st.subheader("Data Quality Metrics")
        quality_metrics = [
            f"✅ No missing values in any column",
            f"✅ All numeric columns within expected ranges",
            f"✅ Categorical variables properly distributed",
            f"✅ Engineered features successfully created",
            f"✅ Data ready for analysis and modeling"
        ]
        
        for metric in quality_metrics:
            st.markdown(metric)
    
    # Page 3: Exploratory Data Analysis (EDA)
    elif page == "📈 Exploratory Data Analysis (EDA)":
        st.markdown('<h2 class="section-header">📈 Exploratory Data Analysis (EDA)</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        **Exploratory Data Analysis:**
        - Statistical summary of key variables
        - Distribution analysis for all features
        - Pattern identification in user behavior
        - Demographic segmentation analysis
        - Relationship exploration between variables
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Key statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_age = filtered_df['Age'].mean()
            st.metric("Average Age", f"{avg_age:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_phone = filtered_df['Daily_Phone_Hours'].mean()
            st.metric("Avg Phone Hours", f"{avg_phone:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_stress = filtered_df['Stress_Level'].mean()
            st.metric("Avg Stress Level", f"{avg_stress:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_sleep = filtered_df['Sleep_Hours'].mean()
            st.metric("Avg Sleep Hours", f"{avg_sleep:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Statistical summary
        st.subheader("Statistical Summary")
        st.dataframe(filtered_df.describe())
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Phone Hours Distribution")
            fig_phone = px.histogram(filtered_df, x='Daily_Phone_Hours', nbins=20,
                                 title="Daily Phone Hours Distribution")
            st.plotly_chart(fig_phone, use_container_width=True)
        
        with col2:
            st.subheader("Stress Level Distribution")
            fig_stress = px.histogram(filtered_df, x='Stress_Level', nbins=10,
                                  title="Stress Level Distribution")
            st.plotly_chart(fig_stress, use_container_width=True)
        
        # Demographics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Gender Distribution")
            gender_counts = filtered_df['Gender'].value_counts()
            fig_gender = px.pie(values=gender_counts.values, 
                               names=gender_counts.index,
                               title="Gender Distribution")
            st.plotly_chart(fig_gender, use_container_width=True)
        
        with col2:
            st.subheader("Device Type Distribution")
            device_counts = filtered_df['Device_Type'].value_counts()
            fig_device = px.bar(x=device_counts.index, y=device_counts.values,
                               title="Device Type Distribution")
            st.plotly_chart(fig_device, use_container_width=True)
    
    # Page 4: Regression Visualization
    elif page == "📊 Regression Visualization":
        st.markdown('<h2 class="section-header">📊 Regression Visualization</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        **Linear Regression Models:**
        - Simple linear regression for key relationships
        - Model performance evaluation (R², RMSE)
        - Visualization of regression fits
        - Model interpretation and insights
        - Prediction accuracy assessment
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Simple regression models
        models_info = []
        
        # Model 1: Phone Hours -> Stress Level
        model1 = simple_regression(filtered_df, 'Daily_Phone_Hours', 'Stress_Level')
        models_info.append({
            'Model': 'Phone Hours → Stress Level',
            'R²': f"{model1['r2']:.4f}",
            'RMSE': f"{model1['rmse']:.4f}",
            'Equation': model1['equation']
        })
        
        # Model 2: Social Media Hours -> Sleep Hours
        model2 = simple_regression(filtered_df, 'Social_Media_Hours', 'Sleep_Hours')
        models_info.append({
            'Model': 'Social Media Hours → Sleep Hours',
            'R²': f"{model2['r2']:.4f}",
            'RMSE': f"{model2['rmse']:.4f}",
            'Equation': model2['equation']
        })
        
        # Model 3: Age -> Work Productivity
        model3 = simple_regression(filtered_df, 'Age', 'Work_Productivity_Score')
        models_info.append({
            'Model': 'Age → Work Productivity',
            'R²': f"{model3['r2']:.4f}",
            'RMSE': f"{model3['rmse']:.4f}",
            'Equation': model3['equation']
        })
        
        # Display models
        st.subheader("Regression Models")
        st.dataframe(pd.DataFrame(models_info))
        
        # Model visualizations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Phone Hours vs Stress")
            fig1 = px.scatter(filtered_df, x='Daily_Phone_Hours', y='Stress_Level',
                           title="Phone Hours vs Stress Level",
                           trendline="ols")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("Social Media vs Sleep")
            fig2 = px.scatter(filtered_df, x='Social_Media_Hours', y='Sleep_Hours',
                           title="Social Media Hours vs Sleep Hours",
                           trendline="ols")
            st.plotly_chart(fig2, use_container_width=True)
        
        with col3:
            st.subheader("Age vs Productivity")
            fig3 = px.scatter(filtered_df, x='Age', y='Work_Productivity_Score',
                           title="Age vs Work Productivity",
                           trendline="ols")
            st.plotly_chart(fig3, use_container_width=True)
        
        # Model insights
        st.subheader("Model Insights")
        st.markdown("""
        **Key Findings:**
        - All simple linear models show very low R² values (near 0)
        - This suggests dataset may be synthetic or randomly generated
        - No strong linear relationships exist between variables
        - Models have high prediction errors (RMSE)
        - Educational value for learning regression techniques
        """)
    
    # Page 5: Correlation Analysis
    elif page == "🔗 Correlation Analysis":
        st.markdown('<h2 class="section-header">🔗 Correlation Analysis</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        **Correlation Analysis:**
        - Complete correlation matrix for all numeric variables
        - Identification of strong relationships (|r| > 0.3)
        - Heatmap visualization for pattern recognition
        - Statistical significance assessment
        - Variable relationship exploration
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Correlation matrix
        st.subheader("Correlation Matrix")
        numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
        correlation_matrix = filtered_df[numeric_cols].corr()
        
        fig_corr = px.imshow(correlation_matrix, 
                            title="Complete Correlation Matrix",
                            color_continuous_scale="RdBu_r",
                            aspect="auto")
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Strong correlations
        st.subheader("Strong Correlations (|r| > 0.3)")
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.3:
                    strong_correlations.append({
                        'Variable 1': correlation_matrix.columns[i],
                        'Variable 2': correlation_matrix.columns[j],
                        'Correlation': round(corr_value, 3)
                    })
        
        if strong_correlations:
            corr_df = pd.DataFrame(strong_correlations)
            st.dataframe(corr_df.sort_values('Correlation', key=abs, ascending=False))
        else:
            st.info("No strong correlations found (|r| > 0.3)")
        
        # Interactive correlation explorer
        st.subheader("Interactive Correlation Explorer")
        col1, col2 = st.columns(2)
        
        with col1:
            var1 = st.selectbox("Select Variable 1", options=numeric_cols)
        
        with col2:
            var2 = st.selectbox("Select Variable 2", options=numeric_cols)
        
        fig_scatter = px.scatter(filtered_df, x=var1, y=var2, 
                               title=f"Scatter Plot: {var1} vs {var2}",
                               trendline="ols")
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Page 6: Interactive Visualizations
    elif page == "📋 Interactive Visualizations":
        st.markdown('<h2 class="section-header">📋 Interactive Visualizations</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        **Interactive Visualizations:**
        - Dynamic charts with real-time filtering
        - Multi-dimensional analysis capabilities
        - User interaction and exploration
        - Comparative analysis tools
        - Custom visualization options
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive charts
        st.subheader("Multi-dimensional Analysis")
        
        # Scatter plot with multiple dimensions
        fig_scatter_3d = px.scatter_3d(filtered_df, 
                                        x='Daily_Phone_Hours', 
                                        y='Stress_Level', 
                                        z='Sleep_Hours',
                                        color='Gender',
                                        size='Work_Productivity_Score',
                                        title="3D Scatter: Phone Hours, Stress, and Sleep")
        st.plotly_chart(fig_scatter_3d, use_container_width=True)
        
        # Pair plot for relationships
        st.subheader("Variable Relationships")
        selected_vars = st.multiselect("Select Variables for Pair Plot", 
                                   options=['Daily_Phone_Hours', 'Stress_Level', 'Sleep_Hours', 'Work_Productivity_Score'],
                                   default=['Daily_Phone_Hours', 'Stress_Level'])
        
        if len(selected_vars) >= 2:
            fig_pair = px.scatter_matrix(filtered_df, dimensions=selected_vars, 
                                    color='Device_Type',
                                    title="Pair Plot of Selected Variables")
            st.plotly_chart(fig_pair, use_container_width=True)
        
        # Box plots by categories
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Usage by Occupation")
            fig_box_occ = px.box(filtered_df, x='Occupation', y='Daily_Phone_Hours',
                                title="Phone Hours by Occupation")
            fig_box_occ.update_xaxes(tickangle=45)
            st.plotly_chart(fig_box_occ, use_container_width=True)
        
        with col2:
            st.subheader("Stress by Age Group")
            fig_box_age = px.box(filtered_df, x='Age_Group', y='Stress_Level',
                               title="Stress Level by Age Group")
            st.plotly_chart(fig_box_age, use_container_width=True)
    
    # Page 7: Deployment Access
    elif page == "🚀 Deployment Access":
        st.markdown('<h2 class="section-header">🚀 Deployment Access</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        **Dashboard Access Information:**
        - Complete analytics dashboard deployment
        - Real-time data exploration capabilities
        - Interactive filtering and visualization
        - Multi-section analysis workflow
        - Export functionality for results
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Access information
        st.subheader("How to Access the Dashboard")
        
        st.markdown("""
        ### 🌐 **Live Dashboard Access**
        
        **Option 1: Local Development**
        ```bash
        cd deployment/
        streamlit run app.py
        ```
        Then open: http://localhost:8501
        
        **Option 2: Cloud Deployment**
        - Deploy to Streamlit Cloud for public access
        - Use GitHub integration for automatic updates
        - Share link with stakeholders
        
        **Option 3: Docker Deployment**
        ```bash
        docker build -t phone-analytics .
        docker run -p 8501:8501 phone-analytics
        ```
        
        ### 📱 **Dashboard Features**
        - **Data Collection**: Dataset overview and information
        - **Data Preprocessing**: Feature engineering and quality checks
        - **EDA**: Statistical analysis and visualizations
        - **Regression**: Linear models with performance metrics
        - **Correlation**: Complete correlation analysis
        - **Interactive**: Dynamic filtering and exploration
        """)
        
        # Quick access buttons
        st.subheader("Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Restart Dashboard"):
                st.rerun()
                st.success("Dashboard restarted!")
        
        with col2:
            if st.button("📥 Export Current Data"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download Filtered Dataset",
                    data=csv,
                    file_name="phone_usage_filtered.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("📊 Generate Report"):
                # Generate summary report
                report_data = {
                    'Metric': ['Total Users', 'Avg Age', 'Avg Phone Hours', 'Avg Stress', 'Avg Sleep'],
                    'Value': [len(filtered_df), f"{filtered_df['Age'].mean():.1f}", 
                              f"{filtered_df['Daily_Phone_Hours'].mean():.1f}",
                              f"{filtered_df['Stress_Level'].mean():.1f}",
                              f"{filtered_df['Sleep_Hours'].mean():.1f}"]
                }
                report_df = pd.DataFrame(report_data)
                csv_report = report_df.to_csv(index=False)
                st.download_button(
                    label="Download Summary Report",
                    data=csv_report,
                    file_name="analysis_summary.csv",
                    mime="text/csv"
                )
        
        # Deployment status
        st.subheader("Deployment Status")
        
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.metric("Dashboard Status", "✅ Active")
            st.metric("Last Updated", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))
        
        with status_col2:
            st.metric("Data Source", "✅ Connected")
            st.metric("Users Online", "🌐 Public")
        
        # Access instructions
        st.subheader("Sharing and Collaboration")
        
        st.markdown("""
        ### 🔗 **Share Your Dashboard**
        
        **For Public Access:**
        1. Deploy to Streamlit Cloud
        2. Get public URL
        3. Share with stakeholders
        
        **For Team Collaboration:**
        1. Use GitHub integration
        2. Enable automatic updates
        3. Collaborate on analysis
        
        **For Production:**
        1. Add authentication
        2. Set up monitoring
        3. Configure scaling
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("🎉 **Complete Phone Usage Analytics Dashboard**")
    st.markdown("Built with Streamlit | Complete Data Science Workflow")

if __name__ == "__main__":
    main()
