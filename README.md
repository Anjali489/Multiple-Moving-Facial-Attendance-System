# Multiple-Moving-Facial-Attendance-System

**   Project Overview

The Multiple Moving Facial Attendance System is an AI-based project designed to automate the attendance process using computer vision and machine learning techniques.
The system detects multiple people in real-time using a webcam and processes each frame to identify human presence.

Currently, the project implements real-time object detection using the YOLOv8 model. Future modules will include tracking, face detection, and facial recognition to mark attendance automatically.


 1.   IMPLEMENTED MODULE
          Object Detection

The current implementation detects persons in real-time from a live camera feed.

For this purpose, the YOLOv8 (You Only Look Once Version 8) model is used. It is a deep learning-based object detection algorithm capable of detecting multiple objects in a single frame efficiently.

The model used in this project is a pre-trained YOLOv8 model trained on the COCO dataset, which contains 80 object classes, including the person class used in this system.

When a person is detected in the camera frame:

A bounding box is generated around the detected person.

The detection is displayed in real-time.

**  Dataset

The project uses the COCO (Common Objects in Context) dataset pre-trained weights provided with YOLOv8.

COCO dataset contains:

80 object classes

Thousands of annotated images

Pre-trained detection capabilities for real-time object recognition.
 
 

The current implementation follows the pipeline below:

Camera Input
↓
Frame Capture
↓
YOLOv8 Object Detection
↓
Person Detection
↓
Bounding Box Generation
↓
Display Output