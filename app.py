import gradio as gr
import requests
import json
import os
from datetime import datetime

class RoleBasedChat:
    def __init__(self):
        self.conversation_history = []
        self.current_role = None
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Role-specific prompts
        self.role_prompts = {
            "Mom 👩‍👧‍👦": {
                "system_prompt": """You are a loving and caring mother. Respond with warmth, patience, and understanding. Give practical advice while showing concern for your child's wellbeing. Use a nurturing tone and always prioritize their happiness and safety. Show motherly care in every response.""",
                "emoji": "🤗"
            },
            "Dad 👨‍👧‍👦": {
                "system_prompt": """You are a wise and supportive father. Provide practical solutions, motivation, and confidence-building advice. Use a slightly serious but caring tone. Share life lessons and help build character. Be the strong pillar of support.""",
                "emoji": "💪"
            },
            "Big Brother 👦": {
                "system_prompt": """You are a cool and understanding big brother. Use casual language, make jokes, but give serious advice when needed. Be protective and supportive. Mix humor with wisdom. Use bro language and be relatable.""",
                "emoji": "😎"
            },
            "Sister 👧": {
                "system_prompt": """You are a sweet and caring sister. Provide emotional support, share gossip, talk about life, fashion, and relationships. Use a loving and understanding tone. Be the person they can share anything with.""",
                "emoji": "💕"
            },
            "Best Friend 👫": {
                "system_prompt": """You are their best friend. Be completely casual and relaxed. Make jokes, have fun, but give honest advice when needed. Use slang, be relatable, and create a judgment-free zone. Be the person they can be themselves with.""",
                "emoji": "🤝"
            },
            "Teacher 👩‍🏫": {
                "system_prompt": """You are a patient and knowledgeable teacher. Explain things clearly, encourage learning, and provide educational guidance. Be supportive but maintain some authority. Help them grow intellectually and personally.""",
                "emoji": "📚"
            },
            "Counselor 🧑‍⚕️": {
                "system_prompt": """You are a professional counselor. Listen actively, provide mental health support, and offer therapeutic guidance. Be empathetic, non-judgmental, and help them process their emotions and thoughts safely.""",
                "emoji": "🎭"
            },
            "Motivational Coach 💪": {
                "system_prompt": """You are an energetic motivational coach. Push them to achieve their goals, provide inspiration, and help build confidence. Use powerful, encouraging language. Be their cheerleader and help them overcome obstacles.""",
                "emoji": "🏆"
            }
        }

    def call_gemini_api(self, user_message, selected_role):
        """
        Call Gemini API using REST endpoint
        """
        if not self.api_key:
            return "❌ Error: GEMINI_API_KEY not found in environment variables. Please set your API key."
        
        try:
            # Get role-specific system prompt
            system_prompt = self.role_prompts[selected_role]["system_prompt"]
            
            # Create conversation context
            conversation_context = self.get_conversation_context()
            
            # Build the full prompt
            full_prompt = f"""{system_prompt}

Previous conversation context:
{conversation_context}

Current user message: {user_message}

Please respond authentically as a {selected_role.split()[0]} would. Stay in character and provide helpful, caring responses."""

            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ]
            }
            
            # Set headers
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.api_key
            }
            
            # Make the API call
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated text
                if 'candidates' in result and len(result['candidates']) > 0:
                    if 'content' in result['candidates'][0]:
                        if 'parts' in result['candidates'][0]['content']:
                            generated_text = result['candidates'][0]['content']['parts'][0]['text']
                            return generated_text
                        else:
                            return "❌ Error: No parts found in response content"
                    else:
                        return "❌ Error: No content found in response"
                else:
                    return "❌ Error: No candidates found in response"
            else:
                error_msg = f"❌ API Error {response.status_code}: {response.text}"
                return error_msg
                
        except requests.exceptions.Timeout:
            return "⏰ Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "🌐 Connection error. Please check your internet connection."
        except requests.exceptions.RequestException as e:
            return f"❌ Request error: {str(e)}"
        except json.JSONDecodeError as e:
            return f"❌ JSON parsing error: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def get_conversation_context(self):
        """Get last few messages for context"""
        if len(self.conversation_history) > 6:
            return "\n".join(self.conversation_history[-6:])
        return "\n".join(self.conversation_history)
    
    def chat_response(self, message, role, history):
        """Handle chat response"""
        if not message.strip():
            return history, ""
        
        # Update current role
        self.current_role = role
        
        # Add user message to history
        history.append([message, None])
        
        # Get AI response using Gemini API
        ai_response = self.call_gemini_api(message, role)
        
        # Update conversation history for context
        self.conversation_history.append(f"User: {message}")
        self.conversation_history.append(f"{role}: {ai_response}")
        
        # Add AI response to chat history
        history[-1][1] = ai_response
        
        return history, ""

# Initialize the chat system
chat_system = RoleBasedChat()

# Create Gradio interface
def create_interface():
    with gr.Blocks(
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            font-family: 'Arial', sans-serif !important;
        }
        .role-selector {
            margin-bottom: 20px;
        }
        .chat-container {
            border-radius: 10px;
            border: 2px solid #e1e5e9;
        }
        .message-box {
            border-radius: 8px;
        }
        .header-info {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .role-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }
        """,
        title="🤖 AI Role Chat - Your Personal AI Assistant"
    ) as demo:
        
        gr.Markdown(
            """
            <div class="header-info">
                <h1>🎭 AI Role Chat Assistant</h1>
                <p><strong>Powered by Google Gemini 2.0 Flash</strong></p>
                <p>Choose your preferred conversation partner and start chatting! Each role brings unique personality and perspective to help you.</p>
            </div>
            """,
            elem_classes="header"
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                role_selector = gr.Radio(
                    choices=list(chat_system.role_prompts.keys()),
                    value="Best Friend 👫",
                    label="🎭 Choose Your AI Role",
                    info="Select who you want to talk to",
                    elem_classes="role-selector"
                )
                
                gr.Markdown(
                    """
                    <div class="role-info">
                        <h3>💡 Available Roles:</h3>
                        <ul>
                            <li><strong>👩‍👧‍👦 Mom</strong> - Caring, nurturing advice</li>
                            <li><strong>👨‍👧‍👦 Dad</strong> - Practical, motivational guidance</li>
                            <li><strong>👦 Big Brother</strong> - Cool, casual support</li>
                            <li><strong>👧 Sister</strong> - Emotional, understanding chat</li>
                            <li><strong>👫 Best Friend</strong> - Fun, judgment-free conversation</li>
                            <li><strong>👩‍🏫 Teacher</strong> - Educational, learning-focused</li>
                            <li><strong>🧑‍⚕️ Counselor</strong> - Professional mental health support</li>
                            <li><strong>💪 Coach</strong> - Motivational and inspiring</li>
                        </ul>
                    </div>
                    """
                )
            
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    height=500,
                    placeholder="👋 Choose a role and start chatting! I'm here to help you in whatever way you need.",
                    elem_classes="chat-container",
                    avatar_images=("👤", "🤖"),
                    bubble_full_width=False
                )
                
                msg_input = gr.Textbox(
                    placeholder="Type your message here... Share anything that's on your mind! 💭",
                    label="Your Message",
                    lines=2,
                    elem_classes="message-box"
                )
                
                with gr.Row():
                    send_btn = gr.Button("Send 📤", variant="primary", scale=2)
                    clear_btn = gr.Button("Clear Chat 🗑️", variant="secondary", scale=1)
        
        # API Status indicator
        with gr.Row():
            api_status = gr.Markdown(
                """
                <div style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    ✅ <strong>Status:</strong> Ready to chat! Make sure your GEMINI_API_KEY is set in environment variables.
                </div>
                """,
                elem_classes="status"
            )
        
        # Event handlers
        def send_message(message, role, history):
            return chat_system.chat_response(message, role, history)
        
        def clear_chat():
            chat_system.conversation_history = []
            return [], ""
        
        def on_role_change(role):
            emoji = chat_system.role_prompts[role]['emoji']
            return f"🎭 **Current Role:** {role} {emoji}\n\nI'm ready to chat with you as your {role.split()[0].lower()}!"
        
        # Button events
        send_btn.click(
            send_message,
            inputs=[msg_input, role_selector, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        msg_input.submit(
            send_message,
            inputs=[msg_input, role_selector, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, msg_input]
        )
        
        # Role change handler
        role_selector.change(
            lambda role: None,  # Just trigger UI update
            inputs=[role_selector]
        )
    
    return demo

# Launch the app
if __name__ == "__main__":
    # Instructions for setting up API key
    print("🚀 Starting AI Role Chat...")
    print("📋 Make sure to set GEMINI_API_KEY environment variable!")
    print("🔗 Get your API key from: https://makersuite.google.com/app/apikey")
    
    demo = create_interface()
    demo.launch(
        share=True,  # Creates public link
        debug=True,
        server_name="0.0.0.0",  # For Hugging Face Spaces
        server_port=7860
    )