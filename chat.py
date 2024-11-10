# import ollama
# import os

# from ollamaHelper import init_responder, responder, clear_messages

# def get_user_input():
#     user_input = input("\n")
#     return user_input

# def start_responder():
#     clear_messages()
#     init_responder(shouldPrint = False)

# def get_response(input):
#     # Translation?
#     response = responder(input, False)
#     return response

# def main():
#     started = False
#     while True:
#         os.system("clear")
#         print("991 Assistant\n",flush = True)
#         user_input = input("> ")
#         if "**START CALL**" in user_input:
#             started = True

#         if started:
#             start_responder()
#         while started:
#             user_input = input("> ")
#             response = get_response(user_input)
#             if response[0] is False:
#                 started = False
#                 break
#             print(response[1])
#         break

# main()
