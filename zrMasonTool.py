import asyncio
import json
import websockets
import requests
import sys
from colorama import Fore, Style

ws_url = "wss://mason-ipv4.zombsroyale.io/gateway/?EIO=4&transport=websocket"

userKey = "3f5caf57f433fc5800304b416305cfe04de2727e7033b5fb"
status = "online"
mode = "Solo"

connect_messages = {
    "setPlat": '42["setPlatform", "android"]',
    "setVer": '42["setVersion", "4.7.0"]',
    "setName": '42["setName", "Player"]',
    "login": f'42["login", "{userKey}"]',
    "status": f'42["setStatus", "{status}"]',
}

party_messages = {
    "createParty": '42["createParty"]',
    "setPartyVer": '42["setPartyVersion", "4.7.0"]',
    "setPartyGMode": f'42["setPartyGameMode", "{mode}"]',
    "setPartyReg": '42["setPartyRegion", "vultr-singapore"]'
}

party_leave_message = '42["leaveParty"]'

async def connect():
    async with websockets.connect(ws_url) as ws:
        for message_type, message in connect_messages.items():
            await ws.send(message)
            print(Fore.YELLOW + f"Sent message: {message}" + Style.RESET_ALL)
            if message_type != "setName":
                response = await ws.recv()
                print(Fore.GREEN + f"Received response: {response}" + Style.RESET_ALL)
        return ws

async def create_party(ws):
    for message_type, message in party_messages.items():
        await ws.send(message)
        if debug_mode:
            print(Fore.YELLOW + f"Sent message: {message}" + Style.RESET_ALL)
            response = await ws.recv()
            print(Fore.GREEN + f"Received response: {response}" + Style.RESET_ALL)
    print(Fore.GREEN + f"{mode}-Party Created" + Style.RESET_ALL)

    global created_party
    created_party = True

    while True:
        print("\n")
        print(Fore.CYAN + "Available actions:")
        print("1 - Leave party")
        print("quit - Quit the program")
        print("\n")

        user_input = input(Fore.WHITE + "Enter action: ")
        if user_input == "1":
            await ws.send(party_leave_message)
            if debug_mode:
                print(Fore.YELLOW + f"Sent message: {party_leave_message}" + Style.RESET_ALL)
                response = await ws.recv()
                print(Fore.GREEN + f"Received response: {response}" + Style.RESET_ALL)
            
            print(Fore.GREEN + "Left party" + Style.RESET_ALL)
            break
        elif user_input == "quit" or user_input == "exit":
            if ws:
                await ws.close()
            sys.exit()
        else:
            print(Fore.RED + "Invalid input, try again" + Style.RESET_ALL)




async def main():
    print(Fore.CYAN +'''
    :::::::::         ::::::::        :::   :::        :::::::::       :::::::: 
          :+:       :+:    :+:       :+:+: :+:+:      :+:    :+:     :+:    :+: 
        +:+        +:+    +:+      +:+ +:+:+ +:+     +:+    +:+     +:+         
      +#+         +#+    +:+      +#+  +:+  +#+     +#++:++#+      +#++:++#++   
    +#+          +#+    +#+      +#+       +#+     +#+    +#+            +#+    
  #+#           #+#    #+#      #+#       #+#     #+#    #+#     #+#    #+#     
#########       ########       ###       ###     #########       ########       
    ''')
    print("\n")
    print("Available actions:")
    print("1 - Connect")
    print("2 - Create Party")
    print("3 - Set Account Key")
    print("debug on/off - Toggle debug mode")
    print("quit - Quit the program")
    print("\n")

    ws = None
    global created_party
    created_party = False
    global debug_mode
    debug_mode = False

    while True:
        user_input = input(Fore.WHITE + "Enter action: ")
        if user_input == "1":
            if ws:
                print(Fore.RED + "Already connected to WebSocket" + Style.RESET_ALL)
            else:
                try:
                    ws = await websockets.connect(ws_url)                    

                    if debug_mode:
                        for message_type, message in connect_messages.items():
                            await ws.send(message)
                            print(Fore.YELLOW + f"Sent message: {message}" + Style.RESET_ALL)
                            if message_type != "setName":
                                response = await ws.recv()
                                print(Fore.GREEN + f"Received response: {response}" + Style.RESET_ALL)
                    print(Fore.GREEN + "WebSocket connected" + Style.RESET_ALL)

                except Exception as e:
                    print(Fore.RED + f"Error connecting to WebSocket: {e}" + Style.RESET_ALL)
        elif user_input == "2":
            try:
                if ws:
                    await create_party(ws)
                else:
                    print(Fore.RED + "Not connected to WebSocket" + Style.RESET_ALL)
            except websockets.exceptions.ConnectionClosedOK:
                print(Fore.RED + "WebSocket connection closed" + Style.RESET_ALL)
                ws = None
        elif user_input == "3":
            userKey = input(Fore.WHITE + "Enter account key: ")

            try:
                r = requests.get(f"https://zombsroyale.io/user/{userKey}")
                if r.status_code != 200:
                    print(Fore.RED + "Invalid UserKey!" + Style.RESET_ALL)
                    continue
            except Exception as e:
                print(Fore.RED + f"Error connecting to API: {e}" + Style.RESET_ALL)
                continue
            friend_code = r.json()['user']['friend_code']
            print(Fore.GREEN + "Valid User Key!" + Style.RESET_ALL)
            connect_messages["login"] = f'42["login", "{userKey}"]'
            print(Fore.GREEN + f"Account Key set (Current Key: '{userKey}') [User:{friend_code}]" + Style.RESET_ALL)
        elif user_input == "debug on":
            debug_mode = True
            print(Fore.GREEN + "Debug mode is on." + Style.RESET_ALL)
        elif user_input == "debug off":
            debug_mode = False
            print(Fore.GREEN + "Debug mode is off." + Style.RESET_ALL)
        elif user_input == "quit" or user_input == "exit":
            if ws:
                await ws.close()
            sys.exit()
        else:
            print(Fore.RED + "Invalid input, try again." + Style.RESET_ALL)

asyncio.run(main())