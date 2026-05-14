import requests


def upload_image_to_imagur(image_file):

    url = "https://imagur.org/wp-admin/admin-ajax.php"

    payload = {
        "action": "imagur_upload"
    }

    files = {
        "image": (
            image_file.name,
            image_file,
            image_file.content_type
        )
    }

    headers = {
        'accept': '*/*',
        'origin': 'https://imagur.org',
        'referer': 'https://imagur.org/',
        'user-agent': 'Mozilla/5.0'
    }

    response = requests.post(
        url,
        headers=headers,
        data=payload,
        files=files
    )

    data = response.json()

    """
    response thường dạng:
    {
        "success": true,
        "data": {
            "url": "https://..."
        }
    }
    """

    if not data.get("success"):
        raise Exception("Upload image failed")

    image_url = data["data"]["direct_url"]

    return image_url