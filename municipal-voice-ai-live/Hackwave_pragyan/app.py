
import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()

st.set_page_config(
    page_title="Municipal Voice AI Assistant",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.call-container {
    text-align: center;
    padding: 30px;
    background: #f8f9fa;
    border-radius: 15px;
    margin: 20px 0;
}

.call-button {
    background: linear-gradient(45deg, #28a745, #20c997);
    border: none;
    border-radius: 50%;
    width: 100px;
    height: 100px;
    color: white;
    font-size: 24px;
    cursor: pointer;
    margin: 20px auto;
    display: block;
    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    transition: transform 0.2s;
}

.call-button:hover {
    transform: scale(1.1);
}

.hangup-button {
    background: linear-gradient(45deg, #dc3545, #c82333);
    border: none;
    border-radius: 50%;
    width: 100px;
    height: 100px;
    color: white;
    font-size: 24px;
    cursor: pointer;
    margin: 20px auto;
    display: block;
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
    transition: transform 0.2s;
}

.hangup-button:hover {
    transform: scale(1.1);
}

.status-indicator {
    display: inline-block;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    margin-right: 10px;
}

.status-connected {
    background-color: #28a745;
}

.status-disconnected {
    background-color: #dc3545;
}

.status-connecting {
    background-color: #ffc107;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'call_status' not in st.session_state:
    st.session_state.call_status = "disconnected"  # disconnected, connecting, connected
if 'room_name' not in st.session_state:
    st.session_state.room_name = None
if 'complaints' not in st.session_state:
    st.session_state.complaints = []

def generate_room_name():
    import uuid
    return f"municipal-call-{str(uuid.uuid4())[:8]}"

def get_token(identity, room):
    """Get a LiveKit token from the token server"""
    try:
        response = requests.get(f"http://localhost:5000/token/{identity}/{room}")
        if response.status_code == 200:
            return response.json()['token']
        else:
            st.error("Failed to get authentication token")
            return None
    except Exception as e:
        st.error(f"Token server error: {e}")
        return None

def start_call():
    """Start a new voice call"""
    st.session_state.call_status = "connecting"
    room_name = generate_room_name()
    st.session_state.room_name = room_name
    
    # Get token for the call
    token = get_token("citizen-user", room_name)
    
    if token:
        # In a real implementation, you would connect to LiveKit here
        # For this demo, we'll simulate the connection
        st.session_state.call_status = "connected"
        st.success(f"Connected to room: {room_name}")
        
        # Simulate a complaint being created after a few seconds
        if not hasattr(st.session_state, 'simulated_complaint'):
            st.session_state.simulated_complaint = True
            threading.Timer(5.0, simulate_complaint).start()

def simulate_complaint():
    """Simulate a complaint being created during a call"""
    complaint_id = f"WS20231201-{len(st.session_state.complaints) + 1:04d}"
    st.session_state.complaints.append({
        'id': complaint_id,
        'type': 'Water Supply',
        'description': 'No water for 2 days',
        'location': 'Sector 15, Gandhinagar',
        'status': 'Submitted',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    st.rerun()

def end_call():
    """End the current call"""
    st.session_state.call_status = "disconnected"
    st.session_state.room_name = None
    st.info("Call ended")

def main():
    st.title("🏛️ Municipal Voice AI Assistant")
    st.markdown("### Live Voice Calling System for Citizen Services")
    
    # Call control section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Voice Call")
        
        # Display call status
        status_display = {
            "disconnected": ("Disconnected", "status-disconnected"),
            "connecting": ("Connecting...", "status-connecting"), 
            "connected": ("Connected", "status-connected")
        }
        
        status_text, status_class = status_display[st.session_state.call_status]
        st.markdown(f"""
        <div class="call-container">
            <h3>Call Status: <span class="status-indicator {status_class}"></span>{status_text}</h3>
            {f'<p><strong>Room:</strong> {st.session_state.room_name}</p>' if st.session_state.room_name else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Call controls
        if st.session_state.call_status == "disconnected":
            if st.button("📞 Start Voice Call", use_container_width=True, type="primary"):
                start_call()
        elif st.session_state.call_status == "connecting":
            st.button("⏳ Connecting...", use_container_width=True, disabled=True)
        else:  # connected
            if st.button("📞 End Call", use_container_width=True, type="secondary"):
                end_call()
            
            st.markdown("---")
            st.markdown("**During call instructions:**")
            st.info("""
            - Speak clearly into your microphone
            - Ask about municipal services
            - Report issues with location details
            - The AI will respond and generate complaint IDs
            """)
    
    with col2:
        st.header("Services Available")
        
        services = [
            {"icon": "💰", "name": "Property Tax", "desc": "Tax inquiries, payments, assessment appeals"},
            {"icon": "💧", "name": "Water Services", "desc": "New connections, leak reporting, bill payments"},
            {"icon": "🗑️", "name": "Waste Management", "desc": "Collection complaints, bulk waste pickup"},
            {"icon": "💡", "name": "Street Lights", "desc": "Repair requests, outage reporting"},
            {"icon": "📄", "name": "Certificates", "desc": "Birth, death, and residency certificates"},
            {"icon": "🛣️", "name": "Road Issues", "desc": "Potholes, repairs, maintenance requests"}
        ]
        
        # Display services in a grid
        cols = st.columns(2)
        for i, service in enumerate(services):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="padding: 15px; background: #f0f2f6; border-radius: 10px; margin-bottom: 10px;">
                    <h3>{service['icon']} {service['name']}</h3>
                    <p>{service['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Complaints history
        if st.session_state.complaints:
            st.markdown("---")
            st.subheader("Recent Complaints")
            for complaint in st.session_state.complaints[-3:]:  # Show last 3 complaints
                st.info(f"""
                **ID**: {complaint['id']}  
                **Type**: {complaint['type']}  
                **Location**: {complaint['location']}  
                **Status**: {complaint['status']}  
                **Time**: {complaint['timestamp']}
                """)
    
    # Emergency contacts section
    st.markdown("---")
    st.header("🆘 Emergency Contacts")
    st.error("""
    **24/7 Emergency Numbers:**
    - 🔥 Fire: 101
    - 👮 Police: 100  
    - 🚑 Ambulance: 102
    - 🏛️ Municipal Emergency: 1800-123-4567
    """)

if __name__ == "__main__":
    main()