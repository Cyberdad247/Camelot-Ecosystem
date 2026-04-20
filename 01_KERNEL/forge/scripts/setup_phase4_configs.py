# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import secrets
import string


def generate_key(length=32):
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


def generate_hex_key(length=32):
    return secrets.token_hex(length // 2)


def setup_activepieces():
    path = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\activepieces"
    env_example = os.path.join(path, ".env.example")
    env_file = os.path.join(path, ".env")

    if os.path.exists(env_example):
        with open(env_example, "r") as f:
            content = f.read()

        # Replace placeholders
        content = content.replace("AP_API_KEY=", f"AP_API_KEY={generate_key(32)}")
        content = content.replace("AP_ENCRYPTION_KEY=", f"AP_ENCRYPTION_KEY={generate_hex_key(32)}")
        content = content.replace("AP_JWT_SECRET=", f"AP_JWT_SECRET={generate_key(32)}")
        content = content.replace("AP_POSTGRES_PASSWORD=", "AP_POSTGRES_PASSWORD=camelot_secure_pw")

        with open(env_file, "w") as f:
            f.write(content)
        print("[SUCCESS] activepieces .env generated.")


def setup_superagi():
    path = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\SuperAGI"
    config_template = os.path.join(path, "config_template.yaml")
    config_file = os.path.join(path, "config.yaml")

    if os.path.exists(config_template):
        with open(config_template, "r") as f:
            content = f.read()

        # Replace placeholders
        content = content.replace("YOUR_OPEN_API_KEY", os.environ.get("OPENAI_API_KEY", "YOUR_OPEN_API_KEY"))
        content = content.replace("DB_PASSWORD: password", "DB_PASSWORD: camelot_secure_pw")
        content = content.replace("postgresql://superagi:password", "postgresql://superagi:camelot_secure_pw")
        content = content.replace("JWT_SECRET_KEY: 'secret'", f"JWT_SECRET_KEY: '{generate_key(32)}'")
        content = content.replace(
            "ENCRYPTION_KEY: abcdefghijklmnopqrstuvwxyz123456", f"ENCRYPTION_KEY: {generate_key(32)}"
        )

        with open(config_file, "w") as f:
            f.write(content)
        print("[SUCCESS] SuperAGI config.yaml generated.")


if __name__ == "__main__":
    setup_activepieces()
    setup_superagi()