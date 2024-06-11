import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense # type: ignore
import matplotlib.pyplot as plt

from config.config import config


# Calcul du nombre d'étapes par epoch et de la validation_steps
steps_per_epoch = (config["TRAIN_IMAGES_PER_ENTITIES"] * config["NUM_ENTITIES"]) // config["BATCH_SIZE"]
validation_steps = (config["VALIDATION_IMAGES_PER_ENTITIES"] * config["NUM_ENTITIES"]) // config["BATCH_SIZE"]

# Générer les données avec augmentation
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest')

validation_datagen = ImageDataGenerator(rescale=1. / 255)

# Génération des flux de données pour l'entraînement et la validation
train_generator = train_datagen.flow_from_directory(
    config["TRAIN_IMAGES_PATH"],
    target_size=(150, 150),
    batch_size=config["BATCH_SIZE"],
    class_mode='categorical')

validation_generator = validation_datagen.flow_from_directory(
    config["VALIDATION_IMAGES_PATH"],
    target_size=(150, 150),
    batch_size=config["BATCH_SIZE"],
    class_mode='categorical')

# Modèle CNN
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(512, activation='relu'),
    Dense(config["NUM_ENTITIES"], activation='softmax')
])

# Compilation du modèle
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])


# Fonction génératrice pour train
def train_gen():
    while True:
        x, y = next(train_generator)
        yield x, y


# Fonction génératrice pour validation
def val_gen():
    while True:
        x, y = next(validation_generator)
        yield x, y


# Création des datasets
train_ds = tf.data.Dataset.from_generator(
    train_gen,
    output_types=(tf.float32, tf.float32),
    output_shapes=((None, 150, 150, 3), (None, config["NUM_ENTITIES"]))
)

validation_ds = tf.data.Dataset.from_generator(
    val_gen,
    output_types=(tf.float32, tf.float32),
    output_shapes=((None, 150, 150, 3), (None, config["NUM_ENTITIES"]))
)

# Utilisation de la méthode .repeat() avec les objets tf.data.Dataset
train_ds = train_ds.repeat()
validation_ds = validation_ds.repeat()

# Entraînement du modèle avec les objets tf.data.Dataset
history = model.fit(
    train_ds,
    steps_per_epoch=steps_per_epoch,
    epochs=30,
    validation_data=validation_ds,
    validation_steps=validation_steps
)

# Enregistrer le modèle
model.save(f"./models/{config["MODEL_LAST_VERSION"]}.keras")

"""
evaluation
"""

# Afficher les courbes de précision et de perte
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.plot(epochs, acc, 'bo', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()
