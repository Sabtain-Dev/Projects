# Stock Trend Prediction

## Project Description
This project leverages machine learning and data mining techniques to predict stock trends based on historical data. It utilizes Spark for distributed data processing, Python libraries for data analysis and visualization, and offers both Jupyter Notebook and a web interface for user interaction.

---

## Features
- Real-time stock data fetching using `yfinance`.
- Distributed data processing and machine learning with `PySpark`.
- Supports clustering, regression, and classification algorithms.
- Interactive web application using `Streamlit`.
- Comprehensive data visualization.

---

## Technologies Used
- **Python**: Core programming language.
- **PySpark**: Distributed data processing and machine learning.
- **Streamlit**: For creating the interactive web interface.
- **NumPy, Pandas**: Data manipulation.
- **Matplotlib**: Data visualization.
- **Scikit-learn**: Machine learning models.
- **YFinance**: Real-time stock data retrieval.

---

## File Structure
- `app.py`: Main script for the Streamlit web application.
- `stocktrade.ipynb`: Notebook for data exploration, model training, and testing.
- `requirements.txt`: List of all dependencies.
- `Stock_Predictions_Model.keras`: Pre-trained Keras model file.

---

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd Stock trend prediction
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Jupyter Notebook**:
   - Open `stocktrade.ipynb` in Jupyter Notebook.
   - Execute cells to explore and train the models.

5. **Run the Web Application**:
   ```bash
   streamlit run app.py
   ```
   - Open the generated URL in a web browser to access the app.

---

## How to Use
1. Start the application using the above command.
2. Use the web interface to input stock data or explore preloaded data.
3. Visualize predictions and trends interactively.

---

## Future Enhancements
- Integrate additional financial APIs for broader data coverage.
- Add deep learning models for improved prediction accuracy.
- Enhance UI/UX for better user experience.

---

## Acknowledgments
Thanks to the open-source community for providing valuable libraries like PySpark, Streamlit, and YFinance, which form the backbone of this project.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.