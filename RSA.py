from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import sys

def generate_key_pair(key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    return private_key, private_key.public_key()

def sign_file(file_path, private_key, hash_algorithm):
    with open(file_path, 'rb') as f:
        file_data = f.read()

    if hash_algorithm == "SHA1":
        hash_func = hashes.SHA1()
    elif hash_algorithm == "SHA256":
        hash_func = hashes.SHA256()
    elif hash_algorithm == "MD5":
        hash_func = hashes.MD5()
    else:
        raise ValueError("Thuật toán băm không hợp lệ")

    signature = private_key.sign(
        file_data,
        padding.PSS(
            mgf=padding.MGF1(hash_func),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hash_func
    )

    with open(file_path + ".sig", "wb") as f:
        f.write(signature)

    print(f"Chữ ký đã được lưu vào {file_path}.sig")

def verify_signature(file_path, public_key, hash_algorithm):
    with open(file_path, 'rb') as f:
        file_data = f.read()
               
    with open(file_path + ".sig", "rb") as f:
        signature = f.read()

    if hash_algorithm == "SHA1":
        hash_func = hashes.SHA1()
    elif hash_algorithm == "SHA256":
        hash_func = hashes.SHA256()
    elif hash_algorithm == "MD5":
        hash_func = hashes.MD5()
    else:
        raise ValueError("Thuật toán băm không hợp lệ")

    try:
        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hash_func),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hash_func
        )
        print("Chữ ký hợp lệ!")
    except InvalidSignature:
        print("Chữ ký không hợp lệ!")

if __name__ == "__main__":
    choice = input("Chọn hành động (1: ký, 2: xác minh): ")

    if choice not in ["1", "2"]:
        print("Lựa chọn không hợp lệ")
        sys.exit(1)

    hash_algo = input("Chọn thuật toán băm (SHA1/SHA256/MD5): ")
    hash_algo = hash_algo.upper()
    if hash_algo not in ["SHA1", "SHA256", "MD5"]:
        print("Thuật toán băm không hợp lệ")
        sys.exit(1)

    file_path = input("Nhập đường dẫn của tệp: ")

    if choice == "1":
        private_key, _ = generate_key_pair()
        sign_file(file_path, private_key, hash_algo)
    else:
        _, public_key = generate_key_pair()
        verify_signature(file_path, public_key, hash_algo)