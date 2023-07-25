#  python3 main.py -i image.png -m msg.txt
#  python3 main.py -i stego_image.png -m extracted_message.txt -e
from PIL import Image
import argparse
from cryptography.fernet import Fernet
import base64


def keygen(password):
    enhanced_password = (password * 6)[:32]
    sample_string_bytes = enhanced_password.encode("ascii")
    return base64.b64encode(sample_string_bytes)


def encrypt(message, password):
    key = keygen(password)
    fernet = Fernet(key)
    return fernet.encrypt(message.encode())


def decrypt(message, password):
    key = keygen(password)
    fernet = Fernet(key)
    return fernet.decrypt(message)


class SteganoHider:
    clear_input_path = ""
    corpus_path = ""
    hidden_output_path = "stego_image.png"

    final_binary_message = ""
    image = ""

    hidden_input_path = ""
    revealed_output = ""

    valid = False

    def validate(self, clear_input_path, corpus_path, password="default"):
        # Read the image
        self.image = Image.open(corpus_path)
        width, height = self.image.size

        # Read the message file
        with open(clear_input_path, 'r') as file:
            message = file.read()

        encrypt(message, password)

        # Store the length of the original message as 32-bit binary
        original_message_length = len(message)
        binary_message_length = format(original_message_length, '032b')

        # Convert the message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message)

        # Create the final binary message that includes the length of the original message
        self.final_binary_message = binary_message_length + binary_message

        # Check if the message fits within the image
        if len(self.final_binary_message) > (width * height * 6):
            return False, "Error: The message is too large to hide in the image."
        else:
            return True, "OK"


    def hide_message(self, hidden_output_path, encrypt, passphrase):
        if encrypt:
            self.validate(self.clear_input_path, self.corpus_path, passphrase)

        self.hidden_output_path = hidden_output_path

        # Pad the message to a multiple of 8 bits
        self.final_binary_message += '0' * (8 - (len(self.final_binary_message) % 8))

        # Get the pixel data as a list of RGB tuples
        pixels = list(self.image.getdata())

        new_pixels = []
        binary_index = 0
        for pixel in pixels:
            r, g, b = pixel

            if binary_index < len(self.final_binary_message):
                new_r = (r & 0xfe) | int(self.final_binary_message[binary_index])
                new_g = (g & 0xfe) | int(self.final_binary_message[binary_index + 1]) if binary_index + 1 < len(self.final_binary_message) else g
                new_b = (b & 0xfe) | int(self.final_binary_message[binary_index + 2]) if binary_index + 2 < len(self.final_binary_message) else b
            else:
                break

            new_pixel = (new_r, new_g, new_b)
            new_pixels.append(new_pixel)

            binary_index += 3

        # Create a new image with the hidden message
        stego_image = self.image
        stego_image.putdata(new_pixels)

        # Save the stego image
        stego_image.save(self.hidden_output_path + "")

        return "Message successfully hidden in the image."


    def extract_message(self, hidden_input_path, revealed_output, encrypt, passphrase):
        # Read the image
        image = Image.open(hidden_input_path)

        revealed_output = revealed_output + "_output"

        # Get the pixel data as a list of RGB tuples
        pixels = list(image.getdata())

        binary_message_length = ''
        binary_message = ''
        for pixel in pixels:
            r, g, b = pixel

            # Extract the least significant bits from each channel
            binary_message_length += str(r & 1)
            binary_message_length += str(g & 1)
            binary_message_length += str(b & 1)

            # Check if we have enough bits to reconstruct the original message length
            if len(binary_message_length) >= 32:
                # Convert binary message length to an integer
                original_message_length = int(binary_message_length[:32], 2)
                break

        for pixel in pixels:
            r, g, b = pixel

            # Extract the least significant bits from each channel
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

            if len(binary_message) - 32 >= original_message_length * 8:
                break

        # Convert binary message to text
        message = ''
        for i in range(32, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            message += chr(int(byte, 2))

        if not encrypt:
            passphrase = "default"
        message = decrypt(message, )

        # Write the extracted message to the output file
        with open(revealed_output, 'w') as file:
            file.write(message)

        return True, "Message successfully extracted from the image."


if __name__ == "__main__":
    sh = SteganoHider()


    parser = argparse.ArgumentParser(description="Hide and extract a text file inside a PNG image.")
    parser.add_argument("-m", "--message", help="Path to the message text file.")
    parser.add_argument("-i", "--image", help="Path to the input PNG image.")
    parser.add_argument("-e", "--extract", action="store_true", help="Extract the message from the image.")

    args = parser.parse_args()

    if args.extract:
        if args.image and args.message:
            sh.extract_message(args.image, args.message)
        else:
            print("Error: Please provide both the input image and the output message file paths.")
    else:
        if args.image and args.message:
            sh.hide_message(args.image, args.message)
        else:
            print("Error: Please provide both the input image and the input message file paths.")