import cv2
import numpy as np
from sort import Sort
from pyfirmata2 import Arduino
import time

# Configuration de PyFirmata2
port = Arduino.AUTODETECT
board = Arduino(port)

# Définir les broches pour les LEDs et le moteur
led_red = 13     # Broche de la LED rouge
led_green = 12   # Broche de la LED verte
motor_pin = 11   # Broche du moteur (PWM)

# Initialiser les LEDs et le moteur
board.digital[led_red].write(0)    # Éteindre la LED rouge au démarrage
board.digital[led_green].write(0)  # Éteindre la LED verte au démarrage
board.digital[motor_pin].write(0)  # Désactiver le moteur au démarrage

# Charger le modèle YOLO
model_config = "yolov3.cfg"
model_weights = "yolov3.weights"
model_classes = "coco.names"

net = cv2.dnn.readNetFromDarknet(model_config, model_weights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

with open(model_classes, "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Index de la classe "person" dans COCO
person_class_id = classes.index("person")

# Initialise le tracker Sort
tracker = Sort()

# Variables pour compter les piétons
line_position = 300  # Position de la ligne d'intersection (pixels)
pedestrian_count = 0
crossed_ids = set()  # Garde les IDs des personnes ayant franchi la ligne
last_command_time = time.time()  # Garde la trace de la dernière commande envoyée

# Fonction pour dessiner la ligne et afficher le comptage
def draw_line_and_count(frame, count):
    height, width, _ = frame.shape
    cv2.line(frame, (0, line_position), (width, line_position), (0, 0, 255), 2)
    cv2.putText(frame, f"Count: {count}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Fonction pour détecter les objets
def detect_objects(frame):
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getUnconnectedOutLayersNames()
    detections = net.forward(layer_names)

    height, width = frame.shape[:2]
    boxes = []
    confidences = []
    class_ids = []

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = int(scores.argmax())
            confidence = scores[class_id]

            if confidence > 0.5 and class_id == person_class_id:
                box = obj[0:4] * np.array([width, height, width, height])
                (center_x, center_y, w, h) = box.astype("int")
                x = int(center_x - (w / 2))
                y = int(center_y - (h / 2))

                boxes.append([x, y, int(w), int(h)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    return boxes, confidences, class_ids

# Activer les LEDs et le moteur en fonction du nombre de piétons détectés
def control_hardware(pedestrians):
    global last_command_time
    current_time = time.time()

    # Vérifiez si 30 secondes se sont écoulées depuis la dernière commande
    if current_time - last_command_time >= 30:
        if pedestrians > 10:
            board.digital[led_red].write(1)   # Allumer la LED rouge
            board.digital[led_green].write(0) # Éteindre la LED verte
            board.digital[motor_pin].write(1) # Activer le moteur
        else:
            board.digital[led_red].write(0)   # Éteindre la LED rouge
            board.digital[led_green].write(1) # Allumer la LED verte
            board.digital[motor_pin].write(0) # Désactiver le moteur
        
        # Mettre à jour le temps de la dernière commande
        last_command_time = current_time

# Capture vidéo
cap = cv2.VideoCapture(0)  # Utiliser "video.mp4" pour une vidéo pré-enregistrée

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Détection des objets
        boxes, confidences, class_ids = detect_objects(frame)
        dets = []

        for i, box in enumerate(boxes):
            x, y, w, h = box
            dets.append([x, y, x+w, y+h, confidences[i]])

        # Mise à jour du tracker
        dets = np.array(dets)
        tracks = tracker.update(dets)

        # Vérification des franchissements
        for track in tracks:
            x1, y1, x2, y2, track_id = track
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # Dessiner les rectangles et l'ID
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {int(track_id)}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Vérifier si l'objet franchit la ligne
            if cy > line_position and int(track_id) not in crossed_ids:
                pedestrian_count += 1
                crossed_ids.add(int(track_id))

        # Contrôler les LEDs et le moteur
        control_hardware(pedestrian_count)

        # Dessiner la ligne et afficher le comptage
        draw_line_and_count(frame, pedestrian_count)

        # Afficher la vidéo
        cv2.imshow("YOLO - Counting Pedestrians", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    board.exit()
