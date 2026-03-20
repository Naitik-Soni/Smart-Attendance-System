#### High level structure
```
face-attendance-system/
│
├── face-service/
│   ├── app/
│   ├── models/
│   ├── requirements.txt
│   └── Dockerfile
│
├── main-service/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

#### Face service structure
```
face-service/
│
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   │
│   ├── face/
│   │   ├── detector.py
│   │   ├── aligner.py
│   │   ├── embedder.py
│   │   └── matcher.py
│   │
│   ├── storage/
│   │   └── embedding_store.py
│   │
│   └── config.py
│
├── models/
│   ├── arcface.onnx
│   └── retinaface.onnx
│
├── requirements.txt
└── Dockerfile
```

#### Main service structure
```
main-service/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── attendance_routes.py
│   │   └── user_routes.py
│   │
│   ├── services/
│   │   ├── attendance_service.py
│   │   └── user_service.py
│   │
│   ├── clients/
│   │   └── face_client.py
│   │
│   └── config.py
│
├── database/
│   ├── models.py
│   └── session.py
│
├── requirements.txt
└── Dockerfile
```