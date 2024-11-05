import os
import base64
import binascii
import marshal
import zlib
import pickle
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import io
import uu
import requests
import subprocess
import time
import sys
import random
import pyfiglet
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

def clear_console():
    """Clear the console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_gradient_banner(text):
    """Create a gradient banner from the provided text using a random font."""
    fonts = ['slant', 'banner3-D', 'block', 'digital', 'banner', 'isometric1']
    selected_font = random.choice(fonts)
    banner = pyfiglet.figlet_format(text, font=selected_font).splitlines()
    
    colors = [Fore.GREEN + Style.BRIGHT, Fore.YELLOW + Style.BRIGHT, Fore.RED + Style.BRIGHT]
    total_lines = len(banner)
    section_size = total_lines // len(colors)
    
    for i, line in enumerate(banner):
        if i < section_size:
            print(colors[0] + line)
        elif i < section_size * 2:
            print(colors[1] + line)
        else:
            print(colors[2] + line)

def gradient_text(text, colors):
    """Apply a gradient to the text using the provided list of colors."""
    gradient_output = ""
    for i, char in enumerate(text):
        gradient_output += colors[i % len(colors)] + char
    return gradient_output

def display_banner_and_social():
    clear_console()
    create_gradient_banner(banner_text)
    print(gradient_text("Follow us on:", [Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX]))
    for platform_name, username in social_media_usernames:
        print(f"{Fore.CYAN}{platform_name + ':'} {Fore.GREEN}{username}")

def check_for_updates():
    print(Fore.YELLOW + "Checking for updates...")
    repo_url = 'BLACK-NINJA-PK/Encoder-Decoder'
    api_url = f'https://api.github.com/repos/{repo_url}/commits/main'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        latest_commit = response.json().get('sha')
        
        try:
            current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()
        except subprocess.CalledProcessError:
            print(Fore.RED + "Error: Could not retrieve the current commit. Are you in a Git repository?")
            return

        if latest_commit != current_commit:
            print(Fore.RED + "New update available. Updating...")
            update_script()
        else:
            print(Fore.GREEN + "Your script is up to date.")
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to check for updates: {e}")

def update_script():
    try:
        subprocess.run(["git", "pull"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(Fore.GREEN + "Script updated successfully!")
        time.sleep(2)
        print(Fore.CYAN + f"\nTo run the script again, use the command:\npython {os.path.basename(__file__)}")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Failed to update the script: {e}")
    except PermissionError:
        print(Fore.RED + "Permission denied. Try running the script with elevated permissions (e.g., 'sudo').")

# Padding function for AES encryption (AES requires data to be a multiple of 16 bytes)
def pad(data):
    padding_length = 16 - (len(data) % 16)
    return data + (chr(padding_length) * padding_length).encode()

def unpad(data):
    return data[:-data[-1]]

# Encoding functions
def en_base2(data):
    return "0" + bin(int(binascii.hexlify(data), 16))[2:]

def en_base16(data):
    return base64.b16encode(data).decode()

def en_base32(data):
    return base64.b32encode(data).decode()

def en_base58(data):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    num = int.from_bytes(data, 'big')
    encoded = ""
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded = alphabet[remainder] + encoded
    return encoded

def en_base64(data):
    return base64.b64encode(data).decode()

def en_urlsafe_base64(data):
    return base64.urlsafe_b64encode(data).decode()

def en_marshal(data):
    code = compile(data, '<string>', 'exec')
    return marshal.dumps(code)

def en_rot13(data):
    return data.translate(str.maketrans(
        b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        b'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))

def en_zlib_base64(data):
    compressed_data = zlib.compress(data)
    return base64.b64encode(compressed_data).decode()

def en_uuencode(data):
    encoded_io = io.BytesIO()
    uu.encode(io.BytesIO(data), encoded_io, name='encoded_file')
    return encoded_io.getvalue().decode()

def en_hex(data):
    return data.hex()

def en_xor_base64(data, key=0x42):
    xor_encoded = ''.join(chr(byte ^ key) for byte in data)
    return base64.b64encode(xor_encoded.encode()).decode()

def en_pickle_base64(data):
    return base64.b64encode(pickle.dumps(data)).decode()

def en_aes_base64_cfb(data):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CFB)
    ciphertext = cipher.encrypt(data)
    encoded = base64.b64encode(cipher.iv + ciphertext).decode()
    return encoded, key

def en_aes_base64_cbc(data):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    padded_data = pad(data)
    encrypted_data = cipher.encrypt(padded_data)
    encrypted_base64 = base64.b64encode(iv + encrypted_data).decode()
    return encrypted_base64, key

def encode_file(file_path, encoding_type):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()

        # Encoding and exec_code creation
        if encoding_type == "b2":
            encoded_data = en_base2(data)
            exec_code = f'print("{encoded_data}")'
        elif encoding_type == "b16":
            encoded_data = en_base16(data)
            exec_code = f'import base64\nexec(base64.b16decode("{encoded_data}".encode()).decode())'
        elif encoding_type == "b32":
            encoded_data = en_base32(data)
            exec_code = f'import base64\nexec(base64.b32decode("{encoded_data}".encode()).decode())'
        elif encoding_type == "b58":
            encoded_data = en_base58(data)
            exec_code = f'print("{encoded_data}")'
        elif encoding_type == "b64":
            encoded_data = en_base64(data)
            exec_code = f'import base64\nexec(base64.b64decode("{encoded_data}".encode()).decode())'
        elif encoding_type == "urlsafe_b64":
            encoded_data = en_urlsafe_base64(data)
            exec_code = f'import base64\nexec(base64.urlsafe_b64decode("{encoded_data}".encode()).decode())'
        elif encoding_type == "marshal":
            code_object = en_marshal(data.decode())
            exec_code = f'import marshal\nexec(marshal.loads({repr(code_object)}))'
        elif encoding_type == "rot13":
            encoded_data = en_rot13(data)
            exec_code = f'exec("{encoded_data}")'
        elif encoding_type == "zlib_base64":
            encoded_data = en_zlib_base64(data)
            exec_code = f'import zlib, base64; exec(zlib.decompress(base64.b64decode("{encoded_data}")).decode())'
        elif encoding_type == "uuencode":
            encoded_data = en_uuencode(data)
            exec_code = f'import uu, io; decoded_io = io.StringIO("""{encoded_data}"""); uu.decode(decoded_io, sys.stdout)'
        elif encoding_type == "hex":
            encoded_data = en_hex(data)
            exec_code = f'exec(bytes.fromhex("{encoded_data}").decode())'
        elif encoding_type == "xor_base64":
            encoded_data = en_xor_base64(data)
            exec_code = f'import base64; exec("".join(chr(ord(c) ^ 0x42) for c in base64.b64decode("{encoded_data}".encode()).decode()))'
        elif encoding_type == "pickle_base64":
            encoded_data = en_pickle_base64(data)
            exec_code = f'import pickle, base64; exec(pickle.loads(base64.b64decode("{encoded_data}".encode())))'
        elif encoding_type == "aes_base64_cfb":
            encoded_data, key = en_aes_base64_cfb(data)
            exec_code = f'import base64; from Crypto.Cipher import AES; key={key}; iv_ciphertext=base64.b64decode("{encoded_data}"); iv=iv_ciphertext[:16]; ciphertext=iv_ciphertext[16:]; cipher=AES.new(key, AES.MODE_CFB, iv=iv); exec(cipher.decrypt(ciphertext).decode())'
        elif encoding_type == "aes_base64_cbc":
            encoded_data, key = en_aes_base64_cbc(data)
            key_hex = key.hex()
            exec_code = f'''
import base64
from Crypto.Cipher import AES

def pad(data):
    padding_length = 16 - (len(data) % 16)
    return data + (chr(padding_length) * padding_length).encode()

def unpad(data):
    return data[:-data[-1]]

encrypted_data = base64.b64decode("{encoded_data}")
key = bytes.fromhex("{key_hex}")
iv = encrypted_data[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
original_data = unpad(cipher.decrypt(encrypted_data[16:]))
exec(original_data.decode())
            '''
        else:
            print(Fore.RED + "Error: Unsupported Encoding Type")
            return None

        # Write the encoded file with self-decoding functionality
        base, ext = os.path.splitext(file_path)
        encoded_file = f"{base}.{encoding_type}"
        with open(encoded_file, 'w') as f:
            f.write(f'"""Execute this script to run the original code."""\n')
            f.write(exec_code)
        print(Fore.GREEN + f"Encoded script saved as {encoded_file}")
        return encoded_file

    except FileNotFoundError:
        print(Fore.RED + "Error: File not found. Please check the file path.")
        return None

def main_menu():
    print(Fore.CYAN + "\nEncoding Menu:")
    print(Fore.YELLOW + "1. Binary (Base2)")
    print(Fore.LIGHTGREEN_EX + "2. Base16 (Hexadecimal)")
    print(Fore.LIGHTMAGENTA_EX + "3. Base32")
    print(Fore.LIGHTBLUE_EX + "4. Base58")
    print(Fore.LIGHTCYAN_EX + "5. Base64")
    print(Fore.LIGHTYELLOW_EX + "6. URL-safe Base64")
    print(Fore.LIGHTRED_EX + "7. Marshal (Python bytecode)")
    print(Fore.LIGHTGREEN_EX + "8. ROT13")
    print(Fore.LIGHTMAGENTA_EX + "9. AES Encryption + Base64 (CFB)")
    print(Fore.LIGHTBLUE_EX + "10. AES Encryption + Base64 (CBC)")
    print(Fore.LIGHTCYAN_EX + "11. zlib (Base64)")
    print(Fore.LIGHTYELLOW_EX + "12. UUencode")
    print(Fore.LIGHTRED_EX + "13. Hexadecimal")
    print(Fore.LIGHTGREEN_EX + "14. XOR (Base64)")
    print(Fore.LIGHTMAGENTA_EX + "15. Pickle (Base64)")
    print(Fore.RED + "0. Quit")
    choice = input(" >>  ")
    exec_menu(choice)

def exec_menu(choice):
    encoding_types = {
        '1': "b2",
        '2': "b16",
        '3': "b32",
        '4': "b58",
        '5': "b64",
        '6': "urlsafe_b64",
        '7': "marshal",
        '8': "rot13",
        '9': "aes_base64_cfb",
        '10': "aes_base64_cbc",
        '11': "zlib_base64",
        '12': "uuencode",
        '13': "hex",
        '14': "xor_base64",
        '15': "pickle_base64",
    }
    if choice in encoding_types:
        file_path = input("Enter the path to the file you want to encode: ")
        if os.path.isfile(file_path):
            encode_file(file_path, encoding_types[choice])
        else:
            print(Fore.RED + "Error: File not found.")
    elif choice == '0':
        exit_()
    else:
        print(Fore.RED + "Invalid selection, please try again.")
        main_menu()

def exit_():
    print(Fore.GREEN + "Exiting the program.")
    exit()

# Main execution
banner_text = "NINJA"
social_media_usernames = [
    ("TELEGRAM", "@black_ninja_pk"),
    ("Coder", "@crazy_arain"),
]

display_banner_and_social()

# Check for updates
check_for_updates()

if __name__ == "__main__":
    main_menu()
