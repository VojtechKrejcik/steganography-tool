#  python3 main.py -i image.png -m msg.txt
#  python3 main.py -i stego_image.png -m extracted_message.txt -e
from PIL import Image
import argparse

def hide_message(image_path, message_path):
    # Read the image
    image = Image.open(image_path)
    width, height = image.size

    # Read the message file
    with open(message_path, 'r') as file:
        message = file.read()

    # Store the length of the original message as 32-bit binary
    original_message_length = len(message)
    binary_message_length = format(original_message_length, '032b')

    # Convert the message to binary
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    # Create the final binary message that includes the length of the original message
    final_binary_message = binary_message_length + binary_message

    # Check if the message fits within the image
    if len(final_binary_message) > (width * height * 6):
        print("Error: The message is too large to hide in the image.")
        return

    # Pad the message to a multiple of 8 bits
    final_binary_message += '0' * (8 - (len(final_binary_message) % 8))

    # Get the pixel data as a list of RGB tuples
    pixels = list(image.getdata())

    new_pixels = []
    binary_index = 0
    for pixel in pixels:
        r, g, b = pixel

        if binary_index < len(final_binary_message):
            new_r = (r & 0xfe) | int(final_binary_message[binary_index])
            new_g = (g & 0xfe) | int(final_binary_message[binary_index + 1]) if binary_index + 1 < len(final_binary_message) else g
            new_b = (b & 0xfe) | int(final_binary_message[binary_index + 2]) if binary_index + 2 < len(final_binary_message) else b
        else:
            break

        new_pixel = (new_r, new_g, new_b)
        new_pixels.append(new_pixel)

        binary_index += 3

    # Create a new image with the hidden message
    stego_image = image
    stego_image.putdata(new_pixels)

    # Save the stego image
    stego_image.save("stego_image.png")

    print("Message successfully hidden in the image.")


def extract_message(image_path, output_path):
    # Read the image
    image = Image.open(image_path)

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

            # Reset binary_message_length to extract the actual message
            binary_message_length = binary_message_length[32:]
            break

    for pixel in pixels:
        r, g, b = pixel

        # Extract the least significant bits from each channel
        binary_message += str(r & 1)
        binary_message += str(g & 1)
        binary_message += str(b & 1)

        if len(binary_message) -32 >= original_message_length * 8:
            break

    # Convert binary message to text
    message = ''
    for i in range(32, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        message += chr(int(byte, 2))

    # Write the extracted message to the output file
    with open(output_path, 'w') as file:
        file.write(message)

    print("Message successfully extracted from the image.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hide and extract a text file inside a PNG image.")
    parser.add_argument("-m", "--message", help="Path to the message text file.")
    parser.add_argument("-i", "--image", help="Path to the input PNG image.")
    parser.add_argument("-e", "--extract", action="store_true", help="Extract the message from the image.")

    args = parser.parse_args()

    if args.extract:
        if args.image and args.message:
            extract_message(args.image, args.message)
        else:
            print("Error: Please provide both the input image and the output message file paths.")
    else:
        if args.image and args.message:
            hide_message(args.image, args.message)
        else:
            print("Error: Please provide both the input image and the input message file paths.")