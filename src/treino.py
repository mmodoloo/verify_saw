import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2

# Caminho para o dataset
DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")

# Gerador de imagens com augmentação AGRESSIVA (para dataset pequeno)
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.15,  # Mais dados para treino (85/15 split)
    
    # Augmentação agressiva para criar mais variedade:
    rotation_range=45,        # Rotações maiores
    width_shift_range=0.4,    # Deslocamentos maiores
    height_shift_range=0.4,
    shear_range=0.3,          # Distorções
    zoom_range=0.4,           # Zoom in/out
    horizontal_flip=True,
    vertical_flip=True,       # Peças podem estar em qualquer orientação
    brightness_range=[0.6, 1.4],  # Variações de brilho
    channel_shift_range=40,   # Variações de cor
    fill_mode='reflect'       # Melhor preenchimento das bordas
)

# Gerador para treino (com augmentação)
train_generator = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(224, 224),
    batch_size=16,  # Batch menor para dataset pequeno
    class_mode="categorical",
    subset="training"
)

# Gerador para validação (sem augmentação, só rescale)
val_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.15)
val_generator = val_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(224, 224),
    batch_size=16,
    class_mode="categorical",
    subset="validation"
)

print(f"Encontradas {train_generator.num_classes} classes")
print(f"Imagens de treino: {train_generator.samples}")
print(f"Imagens de validação: {val_generator.samples}")

# TRANSFER LEARNING - Modelo pré-treinado
base_model = MobileNetV2(
    weights='imagenet',      # Pré-treinado em milhões de imagens
    include_top=False,       # Remove a camada de classificação final
    input_shape=(224, 224, 3),
    alpha=0.75               # Versão um pouco menor do modelo
)

# Congela as camadas pré-treinadas inicialmente
base_model.trainable = False

# Constrói o modelo completo
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(train_generator.num_classes, activation='softmax')
])

# Compilação inicial com learning rate baixo
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy", "top_k_categorical_accuracy"]  # Inclui top-k accuracy
)

print("Arquitetura do modelo:")
model.summary()

# FASE 1: Treinamento inicial (camadas congeladas)
print("\n=== FASE 1: Treinamento com base congelada ===")
history_1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=15,  # Mais épocas para dataset pequeno
    verbose=1
)

# FASE 2: Fine-tuning (descongela algumas camadas)
print("\n=== FASE 2: Fine-tuning ===")
base_model.trainable = True

# Congela apenas as primeiras camadas, permite treinar as últimas
for layer in base_model.layers[:-30]:  # Congela todas exceto as últimas 30
    layer.trainable = False

# Recompila com learning rate MUITO baixo para fine-tuning
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),  # 10x menor
    loss="categorical_crossentropy",
    metrics=["accuracy", "top_k_categorical_accuracy"]
)

# Continua o treinamento
history_2 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,  # Menos épocas para fine-tuning
    verbose=1
)

# Salvar modelo treinado
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "modelo")
os.makedirs(MODEL_DIR, exist_ok=True)
model.save(os.path.join(MODEL_DIR, "modelo_pecas_transfer.keras"))

print("\n=== RESULTADOS FINAIS ===")
# Avaliação final
final_loss, final_acc, final_top_k = model.evaluate(val_generator, verbose=0)
print(f"Acurácia final: {final_acc:.1%}")
print(f"Top-5 acurácia: {final_top_k:.1%}")
print(f"Modelo salvo em: modelo/modelo_pecas_transfer.keras")

# Salva também um resumo dos resultados
results_summary = f"""
RESUMO DO TREINAMENTO:
====================
Dataset: {train_generator.num_classes} classes
Imagens de treino: {train_generator.samples}
Imagens de validação: {val_generator.samples}

FASE 1 - Melhores resultados:
Acurácia de treino: {max(history_1.history['accuracy']):.1%}
Acurácia de validação: {max(history_1.history['val_accuracy']):.1%}

FASE 2 - Resultados finais:
Acurácia final: {final_acc:.1%}
Top-5 acurácia: {final_top_k:.1%}

Arquitetura: MobileNetV2 + Transfer Learning
Técnicas utilizadas:
- Data augmentation agressiva
- Transfer learning com ImageNet
- Two-stage training (freeze + fine-tuning)
- Dropout para regularização
"""

with open(os.path.join(MODEL_DIR, "training_summary.txt"), "w", encoding="utf-8") as f:
    f.write(results_summary)

print(f"\nResumo salvo em: modelo/training_summary.txt")