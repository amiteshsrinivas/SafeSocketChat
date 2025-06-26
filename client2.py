from socket import *
from threading import Thread
import sys, time
import ECC
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from message_logger import MessageLogger

class ChatClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.connected = False  # Initialize connected attribute

        # Configure window
        self.title("Entice Chat")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create chat frame
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)

        # Create text display
        self.text_display = ctk.CTkTextbox(self.chat_frame, wrap="word", height=400)
        self.text_display.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        # Create input frame
        self.input_frame = ctk.CTkFrame(self.chat_frame)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Create message input
        self.msg_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message...")
        self.msg_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.msg_input.bind("<Return>", self.send_message)

        # Create send button
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=(0, 0))

        # Status bar
        self.status_bar = ctk.CTkLabel(self, text="Connecting...", anchor="w")
        self.status_bar.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Initialize connection
        self.setup_connection()

    def setup_connection(self):
        """Setup the connection to the server"""
        try:
            # Get connection details
            self.HOST = input('Enter host: ')
            self.PORT = int(input('Enter port: '))
            self.NAME = input('Enter your name: ')
            self.BUFFER_SIZE = 4096
            self.ADDRESS = (self.HOST, self.PORT)

            # Initialize message logger
            self.logger = MessageLogger(self.NAME)

            # Create socket and connect
            self.CLIENT = socket(AF_INET, SOCK_STREAM)
            self.CLIENT.settimeout(10)  # Set timeout for connection
            self.CLIENT.connect(self.ADDRESS)
            self.CLIENT.settimeout(None)  # Remove timeout after connection

            # Generate and exchange keys
            self.public_key_1, self.private_key_1 = ECC.generate_key_pair()
            serialized_public_key_1 = ECC.serialize_public_key(self.public_key_1)

            # Send our public key
            self.CLIENT.send(serialized_public_key_1)
            self.logger.log_public_key(self.public_key_1, is_sent=True)
            print("Sent public key to server")
            
            # Receive peer's public key
            serialized_public_key_2 = self.CLIENT.recv(self.BUFFER_SIZE)
            if not serialized_public_key_2:
                raise ConnectionError("Failed to receive peer's public key")
            print("Received peer's public key")
            
            self.public_key_2 = ECC.deserialize_public_key(serialized_public_key_2)
            self.logger.log_public_key(self.public_key_2, is_sent=False)
            
            # Derive shared key
            self.shared_key_1 = ECC.derive_shared_key(self.private_key_1, self.public_key_2)
            print("Derived shared key")

            # Start receive thread
            self.connected = True
            self.receive_thread = Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()

            # Update status
            self.status_bar.configure(text=f"Connected as {self.NAME}")
            self.text_display.insert("end", f"Welcome {self.NAME}! You are online!\n")
            self.text_display.insert("end", "----------------------------------------\n")

        except ConnectionRefusedError:
            self.status_bar.configure(text="Connection failed: Server is not available")
            self.text_display.insert("end", "Error: Could not connect to server. Please check if the server is running.\n")
            self.after(3000, self.destroy)
        except TimeoutError:
            self.status_bar.configure(text="Connection failed: Server connection timed out")
            self.text_display.insert("end", "Error: Connection to server timed out. Please try again.\n")
            self.after(3000, self.destroy)
        except Exception as e:
            self.status_bar.configure(text=f"Connection failed: {str(e)}")
            self.text_display.insert("end", f"Error: {str(e)}\n")
            self.after(3000, self.destroy)

    def receive_messages(self):
        """Handle receiving messages"""
        while self.connected:
            try:
                encrypted_msg = self.CLIENT.recv(self.BUFFER_SIZE)
                if not encrypted_msg:  # Server disconnected
                    self.handle_disconnection("Server disconnected")
                    break
                try:
                    msg = ECC.decrypt_message(encrypted_msg, self.shared_key_1)
                    self.text_display.insert("end", f"{msg}\n")
                    self.text_display.see("end")
                    self.logger.log_message(msg, encrypted_msg, self.shared_key_1, is_sent=False)
                except Exception as e:
                    print(f"Error decrypting message: {e}")
                    self.logger.log_error(f"Error decrypting message: {e}")
            except ConnectionResetError:
                self.handle_disconnection("Connection lost")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.logger.log_error(f"Error receiving message: {e}")
                continue  # Continue trying to receive messages

    def send_message(self, event=None):
        """Handle sending messages"""
        if not self.connected:
            return
            
        msg = self.msg_input.get()
        if msg:
            self.msg_input.delete(0, "end")
            full_msg = f"{self.NAME}: {msg}"
            try:
                encrypted_msg = ECC.encrypt_message(full_msg, self.shared_key_1)
                self.CLIENT.send(encrypted_msg)
                self.text_display.insert("end", f"{full_msg}\n")
                self.text_display.see("end")
                self.logger.log_message(full_msg, encrypted_msg, self.shared_key_1, is_sent=True)
            except Exception as e:
                print(f"Error sending message: {e}")
                self.text_display.insert("end", f"Error sending message: {str(e)}\n")
                self.text_display.see("end")
                self.logger.log_error(f"Error sending message: {e}")
                self.handle_disconnection("Connection lost while sending message")

    def handle_disconnection(self, reason):
        """Handle disconnection from server"""
        self.connected = False
        self.status_bar.configure(text=f"Disconnected: {reason}")
        self.text_display.insert("end", f"\n{reason}. Please restart the application.\n")
        self.text_display.see("end")
        self.msg_input.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.logger.log_error(f"Disconnected: {reason}")
        try:
            self.CLIENT.close()
        except:
            pass

    def on_closing(self):
        """Handle window closing"""
        self.connected = False
        try:
            self.CLIENT.close()
        except:
            pass
        self.destroy()

if __name__ == "__main__":
    app = ChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
