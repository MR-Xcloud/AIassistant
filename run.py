"""
Main entry point for the Voice Assistant application.
This script provides a simple command-line interface to choose between
different modes of operation.
"""

import os
import sys

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    print("=" * 60)
    print("🤖 VOICE ASSISTANT WITH AZURE SPEECH SERVICES")
    print("=" * 60)

def print_menu():
    """Print the main menu"""
    print("\nPlease select an option:")
    print("1. Start Voice Assistant")
    print("2. Start Enhanced Voice Assistant (with voice changing)")
    print("3. Test Azure Speech Services")
    print("4. Update Website Data")
    print("5. Exit")
    print("\nEnter your choice (1-5): ", end="")

def main():
    """Main function to run the application"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input().strip()
        
        if choice == '1':
            clear_screen()
            print_header()
            print("\nStarting Voice Assistant...\n")
            try:
                from voice_assistant import run_voice_assistant
                run_voice_assistant()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("\nPress Enter to continue...")
                input()
        
        elif choice == '2':
            clear_screen()
            print_header()
            print("\nStarting Enhanced Voice Assistant...\n")
            try:
                from voice_assistant_enhanced import main as run_enhanced
                run_enhanced()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("\nPress Enter to continue...")
                input()
        
        elif choice == '3':
            clear_screen()
            print_header()
            print("\nTesting Azure Speech Services...\n")
            try:
                from test_azure_speech import test_azure_speech
                test_azure_speech()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("\nPress Enter to continue...")
                input()
        
        elif choice == '4':
            clear_screen()
            print_header()
            print("\nUpdating Website Data...\n")
            try:
                from chatbot import load_data
                load_data(force_reload=True)
                print("\nWebsite data updated successfully!")
            except Exception as e:
                print(f"\n❌ Error: {e}")
            print("\nPress Enter to continue...")
            input()
        
        elif choice == '5':
            clear_screen()
            print_header()
            print("\nThank you for using Voice Assistant. Goodbye!\n")
            sys.exit(0)
        
        else:
            print("\n❌ Invalid choice. Press Enter to try again...")
            input()

if __name__ == "__main__":
    main()