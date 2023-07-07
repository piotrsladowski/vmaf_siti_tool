print("Preset as a feature for bitrate")

import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score

class CustomModel:
    def __init__(self):
        self.classification_model = XGBClassifier()
        self.regression_model = XGBRegressor()

    def fit(self, X, y_clas, y_reg):
        self.classification_model.fit(X, y_clas)

        # get predicted classes and add them to the original features
        predicted_classes = self.classification_model.predict(X)
        X_extended = np.c_[X, predicted_classes]

        self.regression_model.fit(X_extended, y_reg)

    def predict(self, X):
        predicted_classes = self.classification_model.predict(X)
        X_extended = np.c_[X, predicted_classes]

        predicted_output_bitrate = self.regression_model.predict(X_extended)
        return predicted_classes, predicted_output_bitrate

data = pd.read_csv('train_data_15_23.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]

features = data[[
    'input_bitrate',
    'si_avg',
    'ti_avg',
    'resolution',
    'si_min',
    'ti_min',
    'vmaf',
    'criticality',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'width',
    'height',
    'duration_original'
]]
targets_classification = data[['preset']]
targets_regression = data[['output_bitrate']]

X_train, X_test, y_train_clas, y_test_clas, y_train_reg, y_test_reg = train_test_split(
    features, targets_classification, targets_regression, test_size=0.2, random_state=42,
)

y_train_clas = y_train_clas.values.reshape(-1, 1)
y_test_clas = y_test_clas.values.reshape(-1, 1)

y_train_reg = y_train_reg.values.reshape(-1, 1)
y_test_reg = y_test_reg.values.reshape(-1, 1)

model = CustomModel()
model.fit(X_train, y_train_clas, y_train_reg)

predicted_classes, predicted_output_bitrate = model.predict(X_train)
mse = mean_squared_error(y_train_reg, predicted_output_bitrate)
print(f"Training regression MSE: {mse}")
print(f"Training regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification training acc", accuracy_score(y_train_clas, predicted_classes))


predicted_classes, predicted_output_bitrate = model.predict(X_test)
mse = mean_squared_error(y_test_reg, predicted_output_bitrate)
print(f"Test regression MSE: {mse}")
print(f"Test regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes))
#########################################################################

for name in dir():
    if not name.startswith('_'):
        del globals()[name]

print("\nBitrate as a feature for preset")

### Predict bitrate and use it as a feature for preset
import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score

class CustomModel:
    def __init__(self):
        self.regression_model = XGBRegressor()
        self.classification_model = XGBClassifier()

    def fit(self, X, y_reg, y_clas):
        self.regression_model.fit(X, y_reg)

        # get predicted output_bitrate and add them to the original features
        predicted_output_bitrate = self.regression_model.predict(X)
        X_extended = np.c_[X, predicted_output_bitrate]

        self.classification_model.fit(X_extended, y_clas)

    def predict(self, X):
        predicted_output_bitrate = self.regression_model.predict(X)
        X_extended = np.c_[X, predicted_output_bitrate]

        predicted_classes = self.classification_model.predict(X_extended)
        return predicted_output_bitrate, predicted_classes

data = pd.read_csv('train_data_15_23.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]

features = data[[
    'input_bitrate',
    'si_avg',
    'ti_avg',
    'resolution',
    'si_min',
    'ti_min',
    'vmaf',
    'criticality',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'width',
    'height',
    'duration_original'
]]
targets_classification = data[['preset']]
targets_regression = data[['output_bitrate']]

X_train, X_test, y_train_clas, y_test_clas, y_train_reg, y_test_reg = train_test_split(
    features, targets_classification, targets_regression, test_size=0.2, random_state=42,
)

y_train_clas = y_train_clas.values.reshape(-1, 1)
y_test_clas = y_test_clas.values.reshape(-1, 1)

y_train_reg = y_train_reg.values.reshape(-1, 1)
y_test_reg = y_test_reg.values.reshape(-1, 1)

model = CustomModel()
model.fit(X_train, y_train_reg, y_train_clas)

predicted_output_bitrate_train, predicted_classes_train = model.predict(X_train)
mse = mean_squared_error(y_train_reg, predicted_output_bitrate_train)
print(f"Training Regression MSE: {mse}")
print(f"Training Regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification training acc", accuracy_score(y_train_clas, predicted_classes_train))

predicted_output_bitrate_test, predicted_classes_test = model.predict(X_test)
mse = mean_squared_error(y_test_reg, predicted_output_bitrate_test)
print(f"est Regression MSE: {mse}")
print(f"Test Regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))
