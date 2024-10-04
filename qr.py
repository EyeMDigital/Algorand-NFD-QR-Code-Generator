import requests
import qrcode
from PIL import Image, ImageDraw
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# NFD API endpoint
NFD_API_URL = "https://api.nf.domains/nfd/"

def get_nfd_info(nfd):
    """
    Retrieves the deposit account and NFD account for a given NFD segment.
    
    Args:
        nfd (str): The full NFD name.
    
    Returns:
        tuple: A tuple containing the deposit account and NFD account.
    """
    base_url = f"{NFD_API_URL}{nfd}"
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        deposit_account = data.get("depositAccount")
        nfd_account = data.get("nfdAccount")
        return deposit_account, nfd_account
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return "HTTP 404", None
        return f"HTTP error occurred: {http_err}", None
    except Exception as err:
        return f"Other error occurred: {err}", None

def add_rounded_corners(image, radius):
    """
    Adds rounded corners to an image.
    
    Args:
        image (PIL.Image): The image to modify.
        radius (int): The radius of the corners.
    
    Returns:
        PIL.Image: The modified image.
    """
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    image.putalpha(mask)
    return image

def generate_qr_code(wallet_address, output_file, logo_file):
    """
    Generates a QR code with a logo in the center.

    Args:
        wallet_address (str): The wallet address for the QR code.
        output_file (str): The output path for the generated QR code.
        logo_file (str): The path to the logo file to place in the center.
    """
    algorand_uri = f"algorand://{wallet_address}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(algorand_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
    img = img.resize((256, 256), Image.LANCZOS)

    # Draw the white circle in the center
    draw = ImageDraw.Draw(img)
    center_radius = 46
    center_x, center_y = img.size[0] // 2, img.size[1] // 2
    draw.ellipse(
        (center_x - center_radius, center_x - center_radius, center_x + center_radius, center_y + center_radius),
        fill=(255, 255, 255, 255)
    )

    # Paste the logo in the center
    logo = Image.open(logo_file)
    logo = logo.resize((90, 90), Image.LANCZOS)
    img.paste(logo, (center_x - 45, center_y - 45), logo)
    
    # Add rounded corners to the final QR code
    img = add_rounded_corners(img, radius=0)
    img.save(output_file)

if __name__ == "__main__":
    # Example usage
    nfd_segment = "eyemdigital.myalgocard.algo"
    deposit_account, nfd_account = get_nfd_info(nfd_segment)

    if deposit_account and deposit_account != "HTTP 404":
        qr_code_path = "example_qr_code.png"
        logo_path = "logo.png"  # Update this to the path of your logo file
        generate_qr_code(deposit_account, qr_code_path, logo_path)
        logging.info(f"QR code saved to {qr_code_path}")
    else:
        logging.error(f"Error retrieving deposit account: {deposit_account}")
