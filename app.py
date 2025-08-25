import os
import streamlit as st
from gradio_client import Client, file as gradio_file
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    st.error(f"Error configuring Gemini API: {str(e)}")

# Set page configuration
st.set_page_config(
    page_title="✨ Fashion AI Studio",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #2D1B69 0%, #8B5A8C 50%, #D63384 100%);
        color: white;
        font-family: 'Arial', sans-serif;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom containers */
    .fashion-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        margin: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .chatbot-container {
        background: linear-gradient(145deg, #8B5A8C, #D63384);
        border-radius: 20px;
        padding: 25px;
        margin: 10px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 40px rgba(214, 51, 132, 0.4);
    }
    
    .tryon-container {
        background: linear-gradient(145deg, #2D1B69, #8B5A8C);
        border-radius: 20px;
        padding: 25px;
        margin: 10px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 40px rgba(45, 27, 105, 0.4);
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FFD700, #FF69B4, #DA70D6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF69B4, #DA70D6);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 105, 180, 0.6);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed #FFD700;
        border-radius: 15px;
        padding: 20px;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 215, 0, 0.5);
        border-radius: 15px;
        color: white;
        padding: 12px;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 215, 0, 0.5);
        border-radius: 15px;
        color: white;
        padding: 10px;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(0, 255, 127, 0.2);
        border: 1px solid #00FF7F;
        border-radius: 10px;
        color: white;
    }
    
    .stError {
        background: rgba(255, 69, 0, 0.2);
        border: 1px solid #FF4500;
        border-radius: 10px;
        color: white;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #FF69B4 !important;
    }
    
    /* Fashion icons */
    .fashion-icon {
        font-size: 2rem;
        margin-right: 10px;
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(45deg, #8B5A8C, #D63384);
        padding: 12px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .bot-message {
        background: linear-gradient(45deg, #2D1B69, #8B5A8C);
        padding: 12px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 80%;
        margin-right: auto;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .section-title {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def get_chatbot_response(user_message):
    """Fetch response from the Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        fashion_prompt = f"""You are Stella, a trendy AI fashion influencer and stylist. 
        Respond to this fashion query with enthusiasm, style tips, and current trends: {user_message}
        Keep your response engaging, fashionable, and helpful. Use emojis appropriately.
        Be concise but informative, and always maintain a positive and encouraging tone."""
        response = model.generate_content(fashion_prompt)
        return response.text
    except Exception as e:
        return f"Oops! Something went wrong with my fashion radar 💫 Error: {str(e)}"

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary directory."""
    if uploaded_file is None:
        return None
    try:
        # Create a temporary file with a proper extension
        file_ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def display_chat_message(role, message):
    """Display a chat message with appropriate styling."""
    if role == "user":
        st.markdown(f'<div class="user-message">💬 <strong>You:</strong> {message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">🌟 <strong>Stella:</strong> {message}</div>', unsafe_allow_html=True)

def main():
    # Initialize session state variables
    if "show_inputs" not in st.session_state:
        st.session_state.show_inputs = True
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "processing" not in st.session_state:
        st.session_state.processing = False

    # Initialize the Gradio client
    try:
        client = Client("yisol/IDM-VTON")
    except Exception as e:
        st.error(f"Failed to connect to virtual try-on service: {str(e)}")
        client = None

    # App header
    st.markdown('<h1 class="main-title">✨ Fashion AI Studio 👗</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #FFD700; margin-bottom: 30px;">Transform your style with AI-powered virtual try-on and fashion advice!</p>', unsafe_allow_html=True)

    # Create two columns for the main content
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="tryon-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title"><span class="fashion-icon">👗</span>Virtual Try-On Studio</h3>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #E6E6FA; margin-bottom: 20px;">Upload your photos and see the magic happen!</p>', unsafe_allow_html=True)
        
        if st.session_state.show_inputs:
            st.markdown("### 📸 Upload Your Images")
            
            # Image upload section
            col_img1, col_img2 = st.columns(2)
            with col_img1:
                human_image = st.file_uploader("✨ Upload Human Image", type=["png", "jpg", "jpeg"], key="human_img")
            with col_img2:
                garment_image = st.file_uploader("👕 Upload Garment Image", type=["png", "jpg", "jpeg"], key="garment_img")
            
            # Garment description
            garment_desc = st.text_input("💭 Describe the Garment", value="A stylish outfit", placeholder="e.g., A beautiful summer dress with floral patterns")
            
            # Generate button
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                generate_btn = st.button("🎨 Generate Magic!", key="tryon_btn", use_container_width=True, 
                                       disabled=st.session_state.processing)
        else:
            # Display generated image
            if st.session_state.generated_image:
                st.markdown("### ✨ Your Fashion Transformation!")
                st.image(st.session_state.generated_image, caption="Your New Look! 💫", use_column_width=True)
                
                # Download button for the generated image
                if os.path.exists(st.session_state.generated_image):
                    with open(st.session_state.generated_image, "rb") as img_file:
                        btn = st.download_button(
                            label="📥 Download Your Look",
                            data=img_file,
                            file_name="fashion_transformation.png",
                            mime="image/png",
                            use_container_width=True
                        )
                
                # Try again button
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    if st.button("🔄 Try Another Look", key="try_again_btn", use_container_width=True):
                        st.session_state.show_inputs = True
                        st.session_state.generated_image = None
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title"><span class="fashion-icon">💬</span>Stella - Your AI Fashion Guru</h3>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #FFE4E1; margin-bottom: 20px;">Ask me anything about fashion, trends, and style! 💅</p>', unsafe_allow_html=True)
        
        # Display chat history
        st.markdown("### 💬 Fashion Chat")
        chat_container = st.container()
        with chat_container:
            # Initial bot message if no chat history
            if not st.session_state.chat_history:
                display_chat_message("bot", "👋 Hey gorgeous! I'm Stella, your personal AI fashion influencer! Ask me about the latest trends, styling tips, or anything fashion-related! ✨")
            
            # Display chat history
            for message in st.session_state.chat_history:
                display_chat_message(message["role"], message["content"])
        
        # Chat input
        user_input = st.text_input("💭 Ask Stella about fashion:", key="chat_input", placeholder="What's trending this season?")
        
        # Send button
        col_send1, col_send2, col_send3 = st.columns([1, 2, 1])
        with col_send2:
            send_btn = st.button("💌 Send to Stella", key="send_btn", use_container_width=True, 
                               disabled=st.session_state.processing)

        # Process chat message
        if send_btn and user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Stella is thinking... 💭"):
                response = get_chatbot_response(user_input)
                st.session_state.chat_history.append({"role": "bot", "content": response})
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Process virtual try-on request
    if 'generate_btn' in locals() and generate_btn and client and not st.session_state.processing:
        if human_image and garment_image:
            st.session_state.processing = True
            human_image_path = save_uploaded_file(human_image)
            garment_image_path = save_uploaded_file(garment_image)

            if human_image_path and garment_image_path:
                with st.spinner("✨ Creating your fashion magic... This might take a moment! 💫"):
                    try:
                        # Call the virtual try-on API
                        result = client.predict(
                            dict={
                                "background": gradio_file(human_image_path),
                                "layers": [],
                                "composite": None
                            },
                            garm_img=gradio_file(garment_image_path),
                            garment_des=garment_desc,
                            is_checked=True,
                            is_checked_crop=False,
                            denoise_steps=30,
                            seed=42,
                            api_name="/tryon"
                        )
                        
                        # Save the result
                        if result and len(result) > 0:
                            st.session_state.generated_image = result[0]
                            st.session_state.show_inputs = False
                            st.success("🎉 Your fashion transformation is ready! Check it out! ✨")
                        else:
                            st.error("Failed to generate image. Please try again.")
                        
                    except Exception as e:
                        st.error(f"Oops! Something went wrong with the fashion magic 💔 Error: {e}")
                    finally:
                        st.session_state.processing = False
                        st.rerun()
            else:
                st.error("Failed to process uploaded images. Please try again.")
                st.session_state.processing = False
        else:
            st.error("Please upload both a human and a garment image to get started! 👗📷")
            st.session_state.processing = False

    # Footera
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #FFD700; font-style: italic; margin-top: 30px;">✨ Made with 💖 for fashion lovers everywhere! Stay stylish! 👗</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
