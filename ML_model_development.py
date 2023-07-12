####################################################################################
# SCENARIO 1: Predict preset and bitrate using only SI, TI values
# Also check which feature use as an input for second one.
####################################################################################

print("====SCENARIO 1: Predict preset and bitrate using only SI, TI values====")
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

data = pd.read_csv('training_data_at_beginning.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf'
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

data = pd.read_csv('training_data_at_beginning.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf'
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
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))


for name in dir():
    if not name.startswith('_'):
        del globals()[name]

#########################################################################################
# SCENARIO 2: Extend input features with video file properties, e.g. resolution, duration
#########################################################################################

print("\n====SCENARIO 2: Extend input features with video file properties, e.g. resolution, duration====")
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

data = pd.read_csv('training_data_at_beginning.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
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

data = pd.read_csv('training_data_at_beginning.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
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
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))



for name in dir():
    if not name.startswith('_'):
        del globals()[name]

#########################################################################################
# SCENARIO 3: Extend input features with TikTok metadata, e.g. number of likes, comments
#########################################################################################

print("\n====SCENARIO 3: Extend input features with TikTok metadata, e.g. number of likes, comments====")
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

data = pd.read_csv('training_data_at_beginning.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
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

data = pd.read_csv('training_data_at_beginning.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
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
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))


for name in dir():
    if not name.startswith('_'):
        del globals()[name]

#########################################################################################
# SCENARIO 4: Remove videos with scenecuts from the training data
#########################################################################################

print("\n====SCENARIO 4: Remove videos with scenecuts from the training data====")
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

data = pd.read_csv('training_data_without_scenecuts.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
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

data = pd.read_csv('training_data_without_scenecuts.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
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
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {__import__('math').sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))



for name in dir():
    if not name.startswith('_'):
        del globals()[name]

#########################################################################################
# SCENARIO 5: Use bitrate as a feature for preset and remove 100 vidoes extracted to test set
#########################################################################################

print("\n====SCENARIO 5: Use bitrate as a feature for preset and remove 100 vidoes extracted to test set====")

import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, accuracy_score

class CustomModel:
    def __init__(self, reg_params=None, clas_params=None):
        if reg_params is None:
            reg_params = {}
        if clas_params is None:
            clas_params = {}
        self.regression_model = XGBRegressor(**reg_params)
        self.classification_model = XGBClassifier(**clas_params)

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


data = pd.read_csv('training_data.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
]]
targets_classification = data[['preset']]
targets_regression = data[['output_bitrate']]

X_train, X_test, y_train_clas, y_test_clas, y_train_reg, y_test_reg = train_test_split(
    features, targets_classification, targets_regression, test_size=0.2, random_state=42,
)

y_train_clas = y_train_clas.values.ravel()
y_test_clas = y_test_clas.values.ravel()

y_train_reg = y_train_reg.values.ravel()
y_test_reg = y_test_reg.values.ravel()

model = CustomModel()

model.fit(X_train, y_train_reg, y_train_clas)

predicted_output_bitrate_train, predicted_classes_train = model.predict(X_train)
mse = mean_squared_error(y_train_reg, predicted_output_bitrate_train)
print(f"Training Regression MSE: {mse}")
print(f"Training Regression RMSE: {np.sqrt(mse)}")
print("Classification training acc", accuracy_score(y_train_clas, predicted_classes_train))

predicted_output_bitrate_test, predicted_classes_test = model.predict(X_test)
mse = mean_squared_error(y_test_reg, predicted_output_bitrate_test)
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {np.sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))


for name in dir():
    if not name.startswith('_'):
        del globals()[name]


"""
Uncomment if you want to perform grid search. It takes a lot of time.
Scroll down to see the results from the result hyperparameter tuning.
#########################################################################################
# SCENARIO 6: Hyperparameter tuning
#########################################################################################

print("\n====SCENARIO 6: Hyperparameter tuning====")

import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, accuracy_score

class CustomModel:
    def __init__(self, reg_params=None, clas_params=None):
        if reg_params is None:
            reg_params = {}
        if clas_params is None:
            clas_params = {}
        self.regression_model = XGBRegressor(**reg_params)
        self.classification_model = XGBClassifier(**clas_params)

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


# define the parameter grid for XGBRegressor
reg_param_grid = {
    "n_estimators": [50, 100, 150, 200, 250, 300, 350],
    "learning_rate": [0.001, 0.01, 0.05, 0.1, 0.2, 0.3],
    "max_depth": [3, 5, 6, 7]
}

# define the parameter grid for XGBClassifier
clas_param_grid = {
    "n_estimators": [50, 100, 150, 200, 250, 300, 350],
    "learning_rate": [0.001, 0.01, 0.05, 0.1, 0.2, 0.3],
    "max_depth": [3, 5, 6, 7]
}

# perform grid search on the models
reg_grid_search = GridSearchCV(XGBRegressor(), param_grid=reg_param_grid, cv=3, scoring='neg_mean_squared_error', verbose=3)
clas_grid_search = GridSearchCV(XGBClassifier(), param_grid=clas_param_grid, cv=3, scoring='accuracy', verbose=3)


data = pd.read_csv('training_data.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
]]
targets_classification = data[['preset']]
targets_regression = data[['output_bitrate']]

X_train, X_test, y_train_clas, y_test_clas, y_train_reg, y_test_reg = train_test_split(
    features, targets_classification, targets_regression, test_size=0.2, random_state=42,
)

y_train_clas = y_train_clas.values.ravel()
y_test_clas = y_test_clas.values.ravel()

y_train_reg = y_train_reg.values.ravel()
y_test_reg = y_test_reg.values.ravel()

# Uncomment to perform grid search

# fit the grid searches
reg_grid_search.fit(X_train, y_train_reg)
clas_grid_search.fit(X_train, y_train_clas)
# print the best parameters
print(f"Best parameters for regression: {reg_grid_search.best_params_}")
print(f"Best parameters for classification: {clas_grid_search.best_params_}")
model = CustomModel(reg_grid_search.best_params_, clas_grid_search.best_params_)
model.fit(X_train, y_train_reg, y_train_clas)


predicted_output_bitrate_train, predicted_classes_train = model.predict(X_train)
mse = mean_squared_error(y_train_reg, predicted_output_bitrate_train)
print(f"Training Regression MSE: {mse}")
print(f"Training Regression RMSE: {np.sqrt(mse)}")
print("Classification training acc", accuracy_score(y_train_clas, predicted_classes_train))

predicted_output_bitrate_test, predicted_classes_test = model.predict(X_test)
mse = mean_squared_error(y_test_reg, predicted_output_bitrate_test)
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {np.sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))
"""


print("\n====SCENARIO 6: Hyperparameter tuning====")

import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, accuracy_score

class CustomModel:
    def __init__(self, reg_params=None, clas_params=None):
        if reg_params is None:
            reg_params = {}
        if clas_params is None:
            clas_params = {}
        self.regression_model = XGBRegressor(**reg_params)
        self.classification_model = XGBClassifier(**clas_params)

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


optimal_reg_params = {
    'n_estimators': 350,
    'learning_rate': 0.2,
    'max_depth': 6
}

optimal_clas_params = {
    'n_estimators': 200,
    'learning_rate': 0.01,
    'max_depth': 3
}


data = pd.read_csv('training_data.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['preset'] <= 5]
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
]]
targets_classification = data[['preset']]
targets_regression = data[['output_bitrate']]

X_train, X_test, y_train_clas, y_test_clas, y_train_reg, y_test_reg = train_test_split(
    features, targets_classification, targets_regression, test_size=0.2, random_state=42,
)

y_train_clas = y_train_clas.values.ravel()
y_test_clas = y_test_clas.values.ravel()

y_train_reg = y_train_reg.values.ravel()
y_test_reg = y_test_reg.values.ravel()

model = CustomModel(optimal_reg_params, optimal_clas_params)

model.fit(X_train, y_train_reg, y_train_clas)

predicted_output_bitrate_train, predicted_classes_train = model.predict(X_train)
mse = mean_squared_error(y_train_reg, predicted_output_bitrate_train)
print(f"Training Regression MSE: {mse}")
print(f"Training Regression RMSE: {np.sqrt(mse)}")
print("Classification training acc", accuracy_score(y_train_clas, predicted_classes_train))

predicted_output_bitrate_test, predicted_classes_test = model.predict(X_test)
mse = mean_squared_error(y_test_reg, predicted_output_bitrate_test)
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {np.sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))

for name in dir():
    if not name.startswith('_'):
        del globals()[name]

#########################################################################################
# SCENARIO 7: Extend number of classes for classification from 6 to 8. Predict test set
#########################################################################################

print("\n====SCENARIO 7: Extend number of classes for classification from 6 to 8. Predict test set====")

import numpy as np
import pandas as pd
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, accuracy_score

class CustomModel:
    def __init__(self, reg_params=None, clas_params=None):
        if reg_params is None:
            reg_params = {}
        if clas_params is None:
            clas_params = {}
        self.regression_model = XGBRegressor(**reg_params)
        self.classification_model = XGBClassifier(**clas_params)

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


optimal_reg_params = {
    'n_estimators': 350,
    'learning_rate': 0.2,
    'max_depth': 6
}

optimal_clas_params = {
    'n_estimators': 200,
    'learning_rate': 0.01,
    'max_depth': 3
}


data = pd.read_csv('training_data.csv', delimiter=';', encoding='utf-8', decimal='.')
data = data[data['vmaf'] >= 1]

features = data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
]]
targets_classification = data[['preset']]
targets_regression = data[['output_bitrate']]

X_train, X_test, y_train_clas, y_test_clas, y_train_reg, y_test_reg = train_test_split(
    features, targets_classification, targets_regression, test_size=0.2, random_state=42,
)

y_train_clas = y_train_clas.values.ravel()
y_test_clas = y_test_clas.values.ravel()

y_train_reg = y_train_reg.values.ravel()
y_test_reg = y_test_reg.values.ravel()

model = CustomModel(optimal_reg_params, optimal_clas_params)

model.fit(X_train, y_train_reg, y_train_clas)

predicted_output_bitrate_train, predicted_classes_train = model.predict(X_train)
mse = mean_squared_error(y_train_reg, predicted_output_bitrate_train)
print(f"Training Regression MSE: {mse}")
print(f"Training Regression RMSE: {np.sqrt(mse)}")
print("Classification training acc", accuracy_score(y_train_clas, predicted_classes_train))

predicted_output_bitrate_test, predicted_classes_test = model.predict(X_test)
mse = mean_squared_error(y_test_reg, predicted_output_bitrate_test)
print(f"Test Regression MSE: {mse}")
print(f"Test Regression RMSE: {np.sqrt(mse)}")
print("Classification test acc", accuracy_score(y_test_clas, predicted_classes_test))


# Load the test data
test_data = pd.read_csv('test_data.csv', delimiter=';', encoding='utf-8', decimal='.')

# Preprocess the test data to match the training data
# This may include filtering, filling missing values, encoding categorical variables, etc.
test_data = test_data[test_data['vmaf'] >= 1]

test_features = test_data[[
    'si_avg',
    'ti_avg',
    'si_min',
    'ti_min',
    'si_std',
    'si_max',
    'ti_std',
    'ti_max',
    'criticality',
    'vmaf',
    'input_bitrate',
    'resolution',
    'width',
    'height',
    'duration_original',
    'year',
    'digg_count',
    'share_count',
    'play_count',
    'comment_count',
    'author_fans',
    'author_following',
    'author_heart',
    'author_video',
    'author_digg',
]]


# Make predictions using the trained model
predicted_output_bitrate, predicted_preset = model.predict(test_features)

# Print or save the predictions as needed
print(predicted_output_bitrate, predicted_preset)



# Create a DataFrame with the predictions and relevant columns
result = pd.DataFrame({
    'video': test_data['video'], 
    'vmaf': test_data['vmaf'],
    'output_bitrate': predicted_output_bitrate, 
    'preset': predicted_preset
})

# Save the DataFrame to a CSV file
result.to_csv('predictions.csv', index=False)
