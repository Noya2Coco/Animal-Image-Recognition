"""
prepare
"""
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# Répertoires contenant les images d'entraînement et de validation
train_dir = 'animals/train'
validation_dir = 'animals/validation'


# Paramètres pour l'entraînement et la validation
batch_size = 20
num_classes = 90  # Nombre total d'animaux
num_train_images_per_class = 48
num_validation_images_per_class = 12

# Calcul du nombre d'étapes par epoch et de la validation_steps
steps_per_epoch = (num_train_images_per_class * num_classes) // batch_size
validation_steps = (num_validation_images_per_class * num_classes) // batch_size

# Générer les données avec augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest')

validation_datagen = ImageDataGenerator(rescale=1./255)

# Génération des flux de données pour l'entraînement et la validation
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(150, 150),
    batch_size=batch_size,
    class_mode='categorical')

validation_generator = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(150, 150),
    batch_size=batch_size,
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
    Dense(num_classes, activation='softmax')
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
    output_shapes=((None, 150, 150, 3), (None, num_classes))
)

validation_ds = tf.data.Dataset.from_generator(
    val_gen,
    output_types=(tf.float32, tf.float32),
    output_shapes=((None, 150, 150, 3), (None, num_classes))
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
model.save('animal_classifier_model.keras')

"""
evaluation
"""
import matplotlib.pyplot as plt

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