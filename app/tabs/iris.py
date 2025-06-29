def run(model, data, processed, iris_col_desc):
    import streamlit as st
    import numpy as np
    import pandas as pd
    import altair as alt

    columns = processed['columns']
    scaler = processed['scaler']
    X_viz = processed['X_viz']
    y_viz = processed['y_viz']

    viz_cols = ['sepal length (cm)', 'sepal width (cm)',
                'petal length (cm)', 'petal width (cm)']
    viz_cols = [col for col in viz_cols if col in columns][:4]

    st.header('Iris Flower Species Classification')
    st.markdown("This app demonstrates a **multiclass classification** task to predict the _species_ of an iris flower using four features: sepal length, sepal width, petal length, and petal width. **Target labels:** Setosa, Versicolor, Virginica. _Dataset: scikit-learn's Iris._")

    st.subheader('Feature Distributions')
    viz_grid = st.columns(len(viz_cols), gap="medium")
    for i, col in enumerate(viz_cols):
        with viz_grid[i]:
            chart = alt.Chart(pd.DataFrame({col: X_viz[col]})).mark_bar().encode(
                alt.X(f"{col}:Q", bin=alt.Bin(maxbins=20), title=col),
                y=alt.Y('count()', title=None),
                tooltip=[col, 'count()']
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)

    left, right = st.columns([1, 1])

    with left:
        st.subheader('Input Features')
        form = st.form('iris_form')
        inputs = {}
        col1, col2 = form.columns(2)
        iris_col_desc = {
            'sepal length (cm)': 'Sepal length in centimeters',
            'sepal width (cm)': 'Sepal width in centimeters',
            'petal length (cm)': 'Petal length in centimeters',
            'petal width (cm)': 'Petal width in centimeters',
        }
        for idx, col in enumerate(columns):
            avg = float(np.mean(X_viz[col]))
            min_val = float(np.min(X_viz[col]))
            max_val = float(np.max(X_viz[col]))
            desc = iris_col_desc.get(col, col.replace('_', ' ').capitalize())
            help_txt = f"{desc[:40]} (default: {avg:.2f})"
            label_txt = col.title()
            if idx % 2 == 0:
                inputs[col] = col1.number_input(
                    label=label_txt,
                    min_value=min_val,
                    max_value=max_val,
                    value=avg,
                    help=help_txt
                )
            else:
                inputs[col] = col2.number_input(
                    label=label_txt,
                    min_value=min_val,
                    max_value=max_val,
                    value=avg,
                    help=help_txt
                )
        _, btn_col, _ = form.columns([1, 1, 1])
        submitted = btn_col.form_submit_button(
            'Classify', type="primary", use_container_width=True)

    with right:
        pred_head_col, pred_val_col = st.columns([2, 1])
        pred_head_col.subheader('Predict Flower Species')
        pred_placeholder = pred_val_col.empty()
        if 'prediction' not in st.session_state:
            st.session_state['prediction'] = None
        if submitted:
            # Scale input features before prediction
            input_arr = np.array([[inputs[c] for c in columns]])
            input_arr_scaled = scaler.transform(input_arr)
            pred = model.predict(input_arr_scaled)
            pred_class = int(np.argmax(pred))
            st.session_state['prediction'] = pred_class
        if st.session_state['prediction'] is not None:
            class_names = list(np.ravel(data['target_names']))
            pred_idx = int(st.session_state['prediction'])
            if 0 <= pred_idx < len(class_names):
                pred_placeholder.success(f"{class_names[pred_idx]}")
            else:
                pred_placeholder.warning("Unknown class prediction")

        pie_data = pd.DataFrame({'Species': y_viz})
        pie_counts = pie_data['Species'].value_counts(
        ).sort_index().reset_index()
        pie_counts.columns = ['Species', 'Count']

        class_names = list(np.ravel(data['target_names']))
        pie_counts['Label'] = pie_counts['Species'].apply(
            lambda i: class_names[int(i)])
        palette = ['#83c9ff', "#F0F089", "#C28EFA"]
        pie_counts['BaseColor'] = [palette[i %
                                           len(palette)] for i in range(len(pie_counts))]

        pred_species = None
        if st.session_state['prediction'] is not None:
            pred_species = int(st.session_state['prediction'])
        pie_counts['Color'] = pie_counts.apply(
            lambda row: 'orange' if pred_species is not None and row['Species'] == pred_species else row['BaseColor'], axis=1)
        pie_chart = alt.Chart(pie_counts).mark_arc(outerRadius=100).encode(
            theta=alt.Theta(field='Count', type='quantitative'),
            color=alt.Color('Label:N', scale=alt.Scale(
                range=palette), legend=alt.Legend(title='Species')),
            tooltip=['Label', 'Count']
        )
        st.altair_chart(pie_chart, use_container_width=True)

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        with st.expander("Model Details"):
            st.markdown('''**Model Overview:**
- This model has 5 layers:
    - 1 input layer (4 features)
    - 3 hidden layers (with 8, 16, and 64 neurons)
    - 1 output layer (3 classes)
- Uses ReLU and Softmax activations
- Loss Function: Sparse Categorical Cross Entropy''')
            param_col, btn_col = st.columns([3, 2])
            with param_col:
                st.markdown("**Total Parameters:** 1,955")
            with btn_col:
                st.link_button('View Model Architecture',
                               'https://github.com/Param302/ScratchNet/blob/main/models/code/ANN_iris.py', use_container_width=True)
    with exp_col2:
        with st.expander('Performance & Training Insights'):
            st.markdown('''<b>Performance Metrics</b>''',
                        unsafe_allow_html=True)
            st.markdown('''
<table>
<thead>
<tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1-score</th></tr>
</thead>
<tbody>
<tr><td>0</td><td>1.00</td><td>1.00</td><td>1.00</td></tr>
<tr><td>1</td><td>0.88</td><td>1.00</td><td>0.93</td></tr>
<tr><td>2</td><td>1.00</td><td>0.93</td><td>0.96</td></tr>
<tr><td colspan="4" style="text-align:center"><b>Accuracy: 97%</b></td></tr>
</tbody>
</table>
''', unsafe_allow_html=True)
            st.image('assets/iris_loss_curve.png', caption='Loss Curve')
