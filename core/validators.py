from django.core.exceptions import ValidationError

MAX_PHOTO_SIZE_MB = 5
ALLOWED_PHOTO_TYPES = ("jpg", "jpeg", "png", "webp")


def validate_photo(file):
    """Allow only JPG, PNG or WebP images up to 5 MB."""
    ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if ext not in ALLOWED_PHOTO_TYPES:
        raise ValidationError("Only JPG, PNG or WebP images are allowed.")
    if file.size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"Photo must be {MAX_PHOTO_SIZE_MB} MB or smaller.")
