### High level idea of the system

**Overall idea**
1.  Input Sources – Cameras / Images / Videos
2. Backend API Layer – Entry point (FastAPI)
3.  Core Processing Layer – Face detection + recognition
4.  Storage Layer – DBs, embeddings, images
5.  Output / Consumers – Alerts, UI, logs, integrations

1️⃣ Input Sources
- What enters the system
- CCTV cameras
- IP cameras
- Uploaded images
- Video streams

2️⃣ Backend API (FastAPI)
- The gatekeeper
- Receives images or handles RTSP video frames
- Validates requests
- Handles authentication
- Routes work to internal services

3️⃣ Core Face System (Brain)
- Detect face
- Align face
- Generate embedding (ArcFace, etc.)
- Compare with stored embeddings
- Decide:
    - Known user
    - Unknown user
    - Low confidence → ignore (false negative preferred)

4️⃣ Storage Layer
Memory of the system
Stores:
- User profiles
- Face images
- Embeddings (vectors)
- Logs & audit trails

👉 Separation here allows:
- Scaling
- Model replacement
- Safer updates

5️⃣ Event / Alert System
Examples:
- Unknown face detected
- Camera stopped sending frames
- Corrupted image
- Repeated access attempts

6️⃣ Consumers / UI
- Optional but future-proof
- Admin dashboard
- Security console
- Mobile app
- External integrations