🏟️ Smart Stadium AI Assistant

A GenAI-powered Smart Stadium Operations platform that enhances tournament experiences through intelligent crowd management, AI decision support, indoor navigation, multilingual assistance, and real-time operational insights.

🚀 Live Demo: Add your Streamlit URL

💻 GitHub Repository: Add your GitHub URL

🎯 Problem Statement

This project was developed to address the Smart Stadiums & Tournament Operations challenge.

The objective is to build a Generative AI-enabled solution that optimizes venue operations while improving the overall experience for:

👥 Fans
🏟️ Stadium Organizers
🤝 Volunteers
🚓 Security Teams
🏥 Emergency Staff

The application combines AI-powered decision making with interactive analytics to support efficient and safer stadium management.

✨ Key Features

(Keep your existing feature table—it already looks excellent.)

🖥️ Application Screenshots

Add screenshots after deployment.

Home	Crowd Dashboard
docs/home.png	docs/dashboard.png
AI Assistant	Analytics
docs/chat.png	docs/analytics.png
Navigation	Incident Report
docs/navigation.png	docs/report.png

(Upload screenshots into a docs/ folder.)

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[User] --> B[Streamlit Web App]

    B --> C[Crowd Monitoring]
    B --> D[Navigation - NetworkX]
    B --> E[Analytics Dashboard]
    B --> F[Fan Assistant]
    B --> G[Volunteer Assistant]
    B --> H[Incident Report]

    F --> I[Groq API - Llama Models]
    G --> I
    H --> I
    C --> I

    I --> J[AI Decision Support & Responses]
```
🧪 Testing

After the improvements you made today, add this section:

The project includes automated testing using pytest.

Tests cover:
- Navigation utilities
- Data loading
- Helper functions
- AI helper functions (mocked API)

Run tests:

pytest tests/ -v

♿ Accessibility

Mention your improvements.

Accessibility enhancements include:

✔ Improved text contrast

✔ Readable AI chat responses

✔ Tooltips for important controls

✔ Larger report fonts

✔ Better widget labels

📈 Future Enhancements

Instead of ending with the license, add:

Live IoT crowd sensors
Real-time CCTV integration
Google Maps indoor navigation
Multi-stadium management
Emergency evacuation simulation
Voice-enabled AI assistant

👩‍💻 Author
Kusumarani

MA English | Aspiring Data Analyst & AI Developer
