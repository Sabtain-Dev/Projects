import numpy as np
import pandas as pd
import yfinance as yf
from keras.models import load_model
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Load the pre-trained model
model = load_model('Stock_Predictions_Model.keras')

# Streamlit app title
st.title('Stock Market Predictor')

# Input for the stock ticker symbol
stock = st.text_input('Enter Stock Symbol', 'GOOG')

# Date range for data
start = '2012-01-01'
end = '2022-12-31'

# Fetch stock data
data = yf.download(stock, start, end)

# Display stock data
st.subheader('Stock Data')
st.write(data)

# Splitting data into training and testing datasets
data_train = pd.DataFrame(data['Close'][0:int(len(data) * 0.80)])
data_test = pd.DataFrame(data['Close'][int(len(data) * 0.80):])

# Scaling data for LSTM model
scaler = MinMaxScaler(feature_range=(0, 1))
past_100_days = data_train.tail(100)
data_test = pd.concat([past_100_days, data_test], ignore_index=True)
data_test_scaled = scaler.fit_transform(data_test)

# Calculate moving averages
st.subheader('Price vs MA50')
ma_50_days = data['Close'].rolling(50).mean()
fig1 = plt.figure(figsize=(10, 6))
plt.plot(ma_50_days, 'r', label='50-day Moving Average')
plt.plot(data['Close'], 'g', label='Closing Price')
plt.legend()
st.pyplot(fig1)

st.subheader('Price vs MA50 vs MA100')
ma_100_days = data['Close'].rolling(100).mean()
fig2 = plt.figure(figsize=(10, 6))
plt.plot(ma_50_days, 'r', label='50-day Moving Average')
plt.plot(ma_100_days, 'b', label='100-day Moving Average')
plt.plot(data['Close'], 'g', label='Closing Price')
plt.legend()
st.pyplot(fig2)

st.subheader('Price vs MA100 vs MA200')
ma_200_days = data['Close'].rolling(200).mean()
fig3 = plt.figure(figsize=(10, 6))
plt.plot(ma_100_days, 'r', label='100-day Moving Average')
plt.plot(ma_200_days, 'b', label='200-day Moving Average')
plt.plot(data['Close'], 'g', label='Closing Price')
plt.legend()
st.pyplot(fig3)

# Prepare data for predictions
x = []
y = []

for i in range(100, data_test_scaled.shape[0]):
    x.append(data_test_scaled[i-100:i])
    y.append(data_test_scaled[i, 0])

x, y = np.array(x), np.array(y)

# Make predictions
predictions = model.predict(x)

# Scale predictions back to original range
scale = 1 / scaler.scale_
predictions = predictions * scale
y = y * scale

# Plot predictions vs original prices
st.subheader('Original Price vs Predicted Price')
fig4 = plt.figure(figsize=(10, 6))
plt.plot(y, 'g', label='Original Price')
plt.plot(predictions, 'r', label='Predicted Price')
plt.legend()
plt.xlabel('Time')
plt.ylabel('Price')
st.pyplot(fig4)
