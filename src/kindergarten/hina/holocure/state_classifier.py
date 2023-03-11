import tensorflow as tf

from kindergarten.hina.common.fold_classifier import ShardClassifier

class StateClassifier(ShardClassifier):

    def create_model(self, state_count):
        INPUT_SHAPE = (128,128,3)
        model = tf.keras.Sequential([
            tf.keras.layers.GaussianNoise(stddev=0.2, input_shape=INPUT_SHAPE),
            tf.keras.layers.Conv2D(filters=3, kernel_size=1, padding='valid', activation='elu'),
            tf.keras.layers.Conv2D(filters=8, kernel_size=5, padding='valid', activation='elu'),
            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
            tf.keras.layers.MaxPooling2D(pool_size=4),
            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
            tf.keras.layers.Conv2D(filters=8, kernel_size=4, padding='valid', activation='elu'),
            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
            tf.keras.layers.MaxPooling2D(pool_size=4),
            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
            tf.keras.layers.Conv2D(filters=32, kernel_size=7, padding='valid', activation='elu'),
            tf.keras.layers.Flatten(activity_regularizer=tf.keras.regularizers.L2(0.001)),
            #tf.keras.layers.Flatten(),
            #tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dense(32, activation='elu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(state_count, activity_regularizer=tf.keras.regularizers.L1(0.001)),
            #tf.keras.layers.Dense(state_count),
            tf.keras.layers.Softmax(),
        ])
        return model

    def compile_model(self, model):
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                      metrics=['accuracy'])
